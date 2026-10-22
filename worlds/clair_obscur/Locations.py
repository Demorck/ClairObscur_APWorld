from collections import defaultdict
from typing import TYPE_CHECKING

from BaseClasses import Location, Region, LocationProgressType
from .Const import BASE_OFFSET, LOCATION_OFFSET, EXCLUDED_SHOPS, MAX_SHOP_SLOT
from .Data import data, ClairObscurLocationData, ClairObscurShopData
from .Options import ExcludeSuperbosses, ExcludeEndlessTower, ExcludeEndgameLocations
from ..generic.Rules import add_rule

if TYPE_CHECKING:
    from . import ClairObscurWorld


class ClairObscurLocation(Location):
    game: str = "Clair Obscur Expedition 33"
    default_item: str | None

    def __init__(
            self,
            player: int,
            name: str,
            code: int,
            parent: Region | None = None,
            default_item_value: str | None = None) -> None:
        super().__init__(player, name, code, parent)
        self.default_item = default_item_value

def shop_location_name(shop: ClairObscurShopData, slot: str) -> str:
    """
    Full name of a shop location, both the id map and the location creation go through here

    Args:
        shop: The shop data to create the location from
        slot: Which slot of the shop to create the location from

    Returns:
        The stringify of the location name
    """
    return f"Merchant ({shop.region}): {shop.name} - {slot}"

def create_shop_location(
        world: "ClairObscurWorld",
        region: Region,
        shop: ClairObscurShopData,
        slot: str) -> ClairObscurLocation:
    """
    Create one shop location and put it in its region

    Returns:
        The created location
    """
    name = shop_location_name(shop, slot)
    location = ClairObscurLocation(world.player, name, world.location_name_to_id[name], region)
    if shop.name in EXCLUDED_SHOPS:
        location.progress_type = LocationProgressType.EXCLUDED

    region.locations.append(location)

    return location

def create_shop_locations(world: "ClairObscurWorld", region: Region, shop: ClairObscurShopData) -> None:
    """
    Create every location of one shop: the fight, the normal slots then the extra ones
    """
    if shop.has_fight:
        fight = create_shop_location(world, region, shop, "Fight")
        if not world.options.fighting_merchant:
            # Vanilla behaviour, beating him just unlocks his extra stock (through AP)
            fight.place_locked_item(world.create_item(shop.unlock_item))

    for i in range(1, world.options.location_per_shop.value + 1):
        create_shop_location(world, region, shop, f"Item {i}")

    if not shop.has_fight:
        return

    for i in range(1, world.options.extra_location_per_shop.value + 1):
        extra = create_shop_location(world, region, shop, f"Extra Item {i}")
        add_rule(extra, lambda state, itm=shop.unlock_item, pl=world.player: state.has(itm, pl))

def create_locations(world: "ClairObscurWorld", regions: dict[str, Region]) -> None:

    #These locations were in data dumps but not confirmed to be either accessible or inaccessible.
    #These will be left in the pool in case they're found in testing, but will contain filler to avoid softlocks.
    # I'm letting this empty, in case of updates
    unconfirmed_location_names = [
    ]

    excluded_types = []
    excluded_conditions = []
    excluded_locations = [
        "Manor: From Stone Wave Cliffs - In the wardrobe",
    ]
    if not world.options.shuffle_free_aim: excluded_conditions.append("Free Aim")
    if not world.options.gestral_shuffle: excluded_conditions.append("Lost Gestral")

    exclusion_level = world.highest_location_level

    if not world.options.gestral_shuffle:
        excluded_types.append("Lost Gestral")

    for region_name, region in regions.items():
        if region_name == "Menu": continue
        is_endless_tower = region_name.startswith("Endless Tower") and region_name != "Endless Tower Superbosses"

        if (world.options.exclude_superbosses == ExcludeSuperbosses.option_excluded and
                region_name == "Endless Tower Superbosses"):
            continue

        if world.options.exclude_endless_tower == ExcludeEndlessTower.option_excluded and is_endless_tower:
            continue

        region_data = data.regions[region_name]
        region_level = region_data.pictos_level
        if (world.options.exclude_endgame_locations == ExcludeEndgameLocations.option_excluded and
                region_level > exclusion_level):
            continue

        if world.options.shopsanity:
            for shop in data.shops_by_region.get(region_name, []):
                create_shop_locations(world, region, shop)

        for location_name in region_data.locations:

            location_data = data.locations[location_name]
            location_level = max(location_data.pictos_level, region_level)
            if (location_data.type in excluded_types or
                    (world.options.exclude_endgame_locations == ExcludeEndgameLocations.option_excluded and
                     location_level > exclusion_level) or
                    location_name in excluded_locations):
                continue

            loc_id = world.location_name_to_id[location_data.name]
            location = ClairObscurLocation(
                world.player,
                location_data.name,
                loc_id,
                region,
                location_data.default_item
            )
            conditions = location_data.condition
            if conditions:
                for cond in conditions:
                    if cond in excluded_conditions: continue
                    amount = conditions[cond]
                    add_rule(location, lambda state, con=cond, pl=world.player, am=amount: state.has(con, pl, am))

            # if location_data.type == "Boss":
            #     location.progress_type = LocationProgressType.PRIORITY

            if location_data.pictos_level > 1:
                #Checks location_data rather than location_level here as this doesn't need to run if there's already
                #a region access rule for pictos level.
                converted_pictos = world.convert_pictos(location_level)
                add_rule(location, lambda state, pl=world.player, pic=converted_pictos:
                    state.has_group("Picto", pl, pic))

            if (world.options.exclude_endgame_locations == ExcludeEndgameLocations.option_filler and
                    location_level >= exclusion_level):
                location.progress_type = LocationProgressType.EXCLUDED

            if world.options.exclude_endless_tower == ExcludeEndlessTower.option_filler and is_endless_tower:
                location.progress_type = LocationProgressType.EXCLUDED

            if (world.options.exclude_superbosses == ExcludeSuperbosses.option_filler and
                    location_data.type == "Superboss"):
                location.progress_type = LocationProgressType.EXCLUDED

            if location_name in unconfirmed_location_names:
                location.progress_type = LocationProgressType.EXCLUDED

            region.locations.append(location)


def offset_location_value(location_id: int) -> int:
    """
    Returns the AP location id for a given location value
    """
    return BASE_OFFSET + LOCATION_OFFSET + location_id

def reverse_offset_location_value(location_id: int) -> int:
    """
    Returns the location value for a given AP location id
    """
    return location_id - BASE_OFFSET - LOCATION_OFFSET


def create_location_name_to_ap_id() -> dict[str, int]:
    """
    Creates a map from item name to their AP item id
    """
    name_to_ap_id = {}
    index = 0
    for location in data.locations.values():
        name_to_ap_id[location.name] = offset_location_value(index)
        index += 1

    for shop in data.shops.values():
        for i in range(1, MAX_SHOP_SLOT + 1):
            name_to_ap_id[shop_location_name(shop, f"Item {i}")] = offset_location_value(index)
            index += 1

        if shop.has_fight:
            name_to_ap_id[shop_location_name(shop, "Fight")] = offset_location_value(index)
            index += 1

            for i in range(1, MAX_SHOP_SLOT + 1):
                name_to_ap_id[shop_location_name(shop, f"Extra Item {i}")] = offset_location_value(index)
                index += 1

    return name_to_ap_id

def create_location_groups(locations: dict[str, ClairObscurLocationData]) -> dict[str, set[str]]:
    groups: dict[str, set[str]] = defaultdict(set)
    for loc in locations.values():
        groups[loc.type].add(loc.name)

    return dict(groups)
