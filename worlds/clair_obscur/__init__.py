from math import ceil
from typing import Any, ClassVar

import settings
from BaseClasses import Tutorial, Location
from Options import OptionError
from worlds.AutoWorld import WebWorld, World
from .const import BASE_OFFSET, MAX_GEAR_LEVEL, GOAL_REGIONS, GOAL_LEVEL_CAPS
from .game_data import data
from .items import create_item_name_to_ap_id, ClairObscurItem, offset_item_value, \
    create_item_groups, reverse_offset_item_value
from .locations import create_location_name_to_ap_id, create_location_groups, create_locations
from .options import OPTIONS_GROUP, ClairObscurOptions, ChromaPackType, MaxEquipLevel, GearScaling, Goal, \
    ExcludeEndgameLocations, CONSUMABLE_ITEMS, DEFAULT_CONSUMABLE_AMOUNT, ConsumableRollType, DEFAULT_FILLER_WEIGHTS, \
    FILLER_ITEMS, DEFAULT_FILLER_SEQUENCE
from .regions import create_regions, connect_regions
from .rules import set_rules

# How many of each item to generate. Anything not here is added only once
ITEM_AMOUNTS = {
    "Progressive Rock": 5,
    "Rock Crystal": 3,
    "Lost Gestral": 9,

    "Shape of Health": 2,
    "Shape of Life": 2,
    "Shape of Energy": 2,
    "Healing Tint Shard": 10,
    "Energy Tint Shard": 10,
    "Revive Tint Shard": 10,
    "Chroma Elixir Shard": 4,

    # Only 15 are possible to get in a normal playthrough (Thank You Update added 5)
    "Perfect Chroma Catalyst": 15
}

class WebClairObscur(WebWorld):
    """
    Webhost for Clair Obscur Expedition 33.
    """

    theme = "stone"

    setup = Tutorial(
        "Multiworld Setup Guide",
        "Setup guide for Clair Obscur Expedition 33.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Démorck"]
    )

    tutorials = [setup]
    option_groups = OPTIONS_GROUP

class ClairObscurSettings(settings.Group):
    """
    Host side settings for Clair Obscur Expedition 33, nothing is needed here
    """

class ClairObscurWorld(World):
    game = "Clair Obscur Expedition 33"
    web = WebClairObscur()
    topology_present = True

    item_pool: list[ClairObscurItem]
    filler_sequence: list[str] = DEFAULT_FILLER_SEQUENCE
    consumables_amounts: dict[str, tuple[int, int]]

    options_dataclass = ClairObscurOptions
    options: ClairObscurOptions

    allow_surplus_items = True

    item_name_to_id = create_item_name_to_ap_id()
    location_name_to_id = create_location_name_to_ap_id()

    item_name_groups = create_item_groups(data.items)
    location_name_groups = create_location_groups(data.locations)

    required_client_version = (0, 6, 3)

    settings: ClassVar[ClairObscurSettings]
    highest_location_level = MAX_GEAR_LEVEL

    @staticmethod
    def convert_pictos(pictos_level: int) -> int:
        # Converts a pictos level into how many pictos are needed to reach it with scale by order received
        return ceil((pictos_level - 1) * 5.8)

    def sphere_ordered_locations(self) -> list[Location]:
        """
        Every filled location of the multiworld in sphere order
        """
        order = getattr(self.multiworld, "clair_obscur_sphere_order", None)
        if order is None:
            order = [location for sphere in self.multiworld.get_spheres() for location in sphere]
            self.multiworld.sphere_ordered_locations = order

        return order

    def generate_early(self) -> None:
        if self.options.max_chroma_pack < self.options.min_chroma_pack:
            self.options.max_chroma_pack.value = self.options.min_chroma_pack.value

        if self.options.max_price_shop < self.options.min_price_shop:
            self.options.max_price_shop.value = self.options.min_price_shop.value

        self.consumables_amounts: dict[str, tuple[int, int]] = {}
        for name in sorted(CONSUMABLE_ITEMS):
            low = self.options.consumable_min.value.get(name, DEFAULT_CONSUMABLE_AMOUNT)
            high = self.options.consumable_max.value.get(name, DEFAULT_CONSUMABLE_AMOUNT)
            self.consumables_amounts[name] = (low, max(low, high))

        weights = { name: DEFAULT_FILLER_WEIGHTS[name] for name in FILLER_ITEMS }
        weights.update(self.options.filler_weights.value)

        self.filler_sequence = [name for name in sorted(weights) for _ in range(weights[name])]
        if not self.filler_sequence:
            raise OptionError("Clair Obscur Expedition 33: every filler weight is 0, at least one has to "
                              "be above it to fill the item pool")

        # Guard is goal.value is empty (one at random)
        if not self.options.goal.value:
            self.options.goal.value = {self.random.choice(sorted(GOAL_REGIONS))}

        self.highest_location_level = MAX_GEAR_LEVEL
        if self.options.exclude_endgame_locations != ExcludeEndgameLocations.option_included:
            self.highest_location_level = max(GOAL_LEVEL_CAPS.get(name, MAX_GEAR_LEVEL)
                                              for name in self.options.goal.value)

    def create_items(self) -> None:
        self.item_pool = []

        excluded_types = ["Journal", "Character", "Trap"]
        if not (self.options.shopsanity and self.options.fighting_merchant): excluded_types.append("Merchant Unlock")
        excluded_names = []
        if not self.options.gestral_shuffle: excluded_names.append("Lost Gestral")
        if not self.options.shuffle_free_aim: excluded_names.append("Free Aim")

        for item_id, item_data in data.items.items():
            if item_data.type in excluded_types or item_data.name in excluded_names:
                continue

            for _ in range(ITEM_AMOUNTS.get(item_data.name, 1)):
                self.item_pool.append(self.create_item_by_id(item_id))

        if self.options.char_shuffle:
            #Create items for characters if character shuffle is on.
            chars = ["Gustave", "Maelle", "Lune", "Sciel", "Monoco", "Verso"]
            starting_char = self.options.starting_char.current_option_name
            for char in chars:
                char_item = self.create_item(char)
                if char == starting_char:
                    self.push_precollected(char_item)
                else:
                    self.item_pool.append(char_item)

        #Add filler to match the amount of locations
        free_locations = len(self.multiworld.get_unfilled_locations(self.player))
        remaining_items_to_generate = free_locations - len(self.item_pool)

        if remaining_items_to_generate < 0:
            raise OptionError(f"Clair Obscur Expedition 33: the item pool holds {len(self.item_pool)} items but only "
                            f"{free_locations} locations are open. Include more locations or pick a further goal"
            )

        trap_chance = self.options.trap_chance
        for i in range(0, remaining_items_to_generate):
            if self.random.randint(1, 100) <= trap_chance:
                #Reference trap weights when more trap types are implemented
                item_name = "Feet Trap"
            else:
                item_name = self.filler_sequence[i % len(self.filler_sequence)]
            self.item_pool.append(self.create_item(item_name))

        self.multiworld.itempool += self.item_pool

    def fill_slot_data(self) -> dict[str, Any]:
        slot_data: dict[str, Any] = {
            "options": self.options.as_dict(
                "goal", "goal_requirement",
                "char_shuffle", "starting_char", "gestral_shuffle", "gear_scaling", "shuffle_free_aim",
                "exclude_endgame_locations", "exclude_endless_tower",

                # Chroma
                "chroma_pack_type", "min_chroma_pack", "max_chroma_pack",

                # SHOP
                "shopsanity", "location_per_shop", "extra_location_per_shop", "show_shop_items", "create_hint",
                "create_hint_extra"
            ),

            "totals": {
                "pictos": len(self.item_name_groups["Picto"]),
                "weapons": len(self.item_name_groups["Weapon"]),
            },
        }

        if self.options.chroma_pack_type == ChromaPackType.option_random_fixed_range:
            slot_data["chroma"] = self.random.randint(self.options.min_chroma_pack.value,
                                                      self.options.max_chroma_pack.value)

        slot_data["consumables"] = self.consumable_slot_data()
        slot_data["max_gear_level"] = self.max_gear_level()
        slot_data["exclusion_level"] = self.highest_location_level
        slot_data.update(self.gear_scaling_slot_data())

        if self.options.shopsanity:
            slot_data["shops"] = self.shop_slot_data()

        return slot_data


    def max_gear_level(self) -> int:
        """
        Return the maximum gear level for this slot based on settings
        """
        if self.options.max_equip_level == MaxEquipLevel.option_custom:
            return self.options.custom_max_equip_level.value

        return self.highest_location_level

    def gear_scaling_slot_data(self) -> dict[str, list[int]]:
        """
        Picto and weapon ids in the order the client should scale them
        """
        match self.options.gear_scaling:
            case GearScaling.option_sphere_placement:
                pictos: list[int] = []
                weapons: list[int] = []
                for location in self.sphere_ordered_locations():
                    item = location.item
                    if item.player != self.player:
                        continue
                    if item.name in self.item_name_groups["Picto"]:
                        pictos.append(item.code)
                    elif item.name in self.item_name_groups["Weapon"]:
                        weapons.append(item.code)

                return {"pictos": pictos, "weapons": weapons}

            case GearScaling.option_balanced_random:
                # shuffling straight from it makes the seed unreproducible, need to sort them before
                pictos = sorted(self.item_name_to_id[name] for name in self.item_name_groups["Picto"])
                weapons = sorted(self.item_name_to_id[name] for name in self.item_name_groups["Weapon"])
                self.random.shuffle(pictos)
                self.random.shuffle(weapons)

                return {"pictos": pictos, "weapons": weapons}

        return {}

    def shop_slot_data(self) -> dict[str, dict[str, list[int]]]:
        shops: dict[str, dict[str, list[int]]] = {}
        low = self.options.min_price_shop.value
        high = self.options.max_price_shop.value

        for shop_name, shop in data.shops.items():
            extra_slots = self.options.extra_location_per_shop.value if shop.has_fight else 0
            shops[shop_name] = {
                "prices": [self.random.randint(low, high) for _ in range(self.options.location_per_shop.value)],
                "extra_prices": [self.random.randint(low, high) for _ in range(extra_slots)],
            }

        return shops

    def consumable_slot_data(self) -> dict[str, list[int]]:
        """
        How much each consumable gives, as a [min, max] the client rolls inside
        A fixed roll is just min == max so the client does the same thing regardless the option
        """
        amounts = {}
        for name, (low, high) in self.consumables_amounts.items():
            if self.options.consumable_roll_type == ConsumableRollType.option_random_fixed_range:
                rolled = self.random.randint(low, high)
                amounts[name] = [rolled, rolled]
            else:
                amounts[name] = [low, high]

        return amounts

    def create_item(self, name: str) -> ClairObscurItem:
        return self.create_item_by_id(reverse_offset_item_value(self.item_name_to_id[name]))

    def create_item_by_id(self, item_id: int) -> ClairObscurItem:
        item_data = data.items[item_id]

        return ClairObscurItem(item_data.name, item_data.classification, offset_item_value(item_id), self.player)

    def get_pre_fill_items(self) -> list[ClairObscurItem]:
        return [self.create_item(self.get_filler_item_name())]

    def get_filler_item_name(self) -> str:
        return self.random.choice(self.filler_sequence)

    def create_regions(self) -> None:
        regions = create_regions(self)
        connect_regions(self)
        create_locations(self, regions)

    def set_rules(self):
        set_rules(self)

