from dataclasses import dataclass
from Options import Choice, PerGameCommonOptions, StartInventory, OptionGroup, Toggle, Range

class Goal(Choice):
    """
    The victory condition for your run
    """

    display_name = "Goal"
    option_paintress = 0
    option_curator = 1
    option_clea = 4
    option_painted_love = 2
    option_simon = 3
    default = 1

class ExcludeEndgameLocations(Choice):
    """
    Determines how to handle locations higher level than the set goal, if the goal is Paintress or Curator.
    Excluded: Locations won't be added to the pool.
    Filler: Locations will only contain filler items.
    Included: All locations are included.
    """
    internal_name = "exclude_endgame_locations"
    display_name = "Exclude Endgame Locations"
    option_excluded = 0
    option_filler = 1
    option_included = 2
    default = 0

class ExcludeEndlessTower(Choice):
    """
    Determines how to handle Endless Tower locations.
    Excluded: Locations won't be added to the pool.
    Filler: Locations will only contain filler items.
    Included: All locations are included.
    """
    internal_name = "exclude_endless_tower"
    display_name = "Exclude Endless Tower"
    option_excluded = 0
    option_filler = 1
    option_included = 2
    default = 0

class ExcludeSuperbosses(Choice):
    """
    Determines how to handle Superbosses (the four in the Endless Tower).
    Excluded: Locations won't be added to the pool.
    Filler: Locations will only contain filler items.
    Included: All locations are included.
    """
    internal_name = "exclude_superbosses"
    display_name = "Exclude Superbosses"
    option_excluded = 0
    option_filler = 1
    option_included = 2
    default = 0

class ShuffleLostGestrals(Toggle):
    """
    Shuffles the lost gestrals into the item pool.
    """
    internal_name = "shuffle_lost_gestrals"
    display_name = "Shuffle Lost Gestrals"

class ShuffleFreeAim(Toggle):
    """
    Shuffles the ability to shoot outside of battle into the pool.
    """
    internal_name = "shuffle_free_aim"
    display_name = "Shuffle Free Aim"
    default = 0

class AreaLogic(Choice):
    """
    Determines how many major area unlock items will be placed how early.
    Normal: Act 1 major areas won't be placed past Act 1; Forgotten Battlefield and Old Lumiere won't be placed behind
    Visages/Sirene; Visages and Sirene won't be placed behind The Monolith.
    Hard: Only half of the major areas will be placed in those segments.
    No Logic: Areas could be anywhere. You may need to grind world map enemies for a long time.
    """
    internal_name = "area_logic"
    display_name = "Area logic"
    option_normal = 1
    option_hard = 2
    option_no_logic = 0
    default = 1

class ShuffleCharacters(Toggle):
    """Shuffles characters into the item pool."""
    display_name = "Shuffle characters"

class StartingCharacter(Choice):
    """Determines which character you start with. Does nothing if Shuffle Characters is set to false."""
    internal_name = "starting_character"
    display_name = "Starting character"
    option_gustave = 0
    option_lune = 1
    option_maelle = 2
    option_sciel = 3
    option_monoco = 4
    option_verso = 5
    default = 0

class GearScaling(Choice):
    """How the levels of pictos and weapons you receive are determined.
    Sphere placement: Roughly scales pictos/weapons by the logical sphere they're placed in.
    Order received: As you receive more pictos/weapons, the levels of the next ones you receive will go up.
    Balanced random: Pictos/weapons have random levels assigned in an even spread.
    Full random: Exaclty what it says. There's no guarantee that you'll get high-level pictos... but you probably will."""
    internal_name = "gear_scaling"
    display_name = "Gear Scaling"
    option_sphere_placement = 0
    option_order_received = 1
    option_balanced_random = 2
    option_full_random = 3
    default = 1

class MaxEquipLevel(Choice):
    """
    What level pictos and weapons received though Archipelago will go up to. Weapons can still be upgraded past this.
    Highest Included Location: The highest level equipment will match the gear you would normally get from the most
    difficult location included in the pool. With endgame locations excluded, this will be 15 with Paintress as your
    goal, 16 for Curator, 28 for Clea, or 33 for Simon or Painted Love.
    Custom: Set a specific level.
    """
    internal_name = "max_level_choice"
    display_name = "Max Equipment Level"
    option_highest_included_location = 0
    option_custom = 1

class CustomMaxEquipLevel(Range):
    """
    What level pictos and weapons received through Archipelago will go up to if Max Equip Level is set to Custom.
    """
    internal_name = "custom_max_equip_level"
    display_name = "Custom Max Equipment Level"
    range_start = 1
    range_end = 33
    default = 33

class TrapChance(Range):
    """
    The chance for any filler item to be replaced with a trap.
    Currently, the only implemented trap is the Feet Trap.
    Feet Trap: plays the "My, what lovely feet" voice line and shows you some feet pics. Are you sure about this....?
    """
    display_name = "Trap Chance"
    range_start = 0
    range_end = 100
    default = 0

class ChromaPackType(Choice):
    """
    Random fixed range: Choses ONE random number between range option. The Chroma pack will always be this value
    Random range: The client chose one random value between the range option. If you rerun the same seed, the client can give different value.
    """
    internal_name = "chroma_pack_type"
    display_name = "Chroma pack type"
    option_random_fixed_range = 0
    option_random_range = 1

class MinChromaPack(Range):
    """
    How much the filler: "Chroma Pack" can give chroma at minimum. If you have Shopsanity, i suggest to have a high range of chroma pack.
    """
    internal_name = "min_chroma_pack"
    display_name = "Min Chroma Pack"
    range_start = 0
    range_end = 100_000
    default = 20_000

class MaxChromaPack(Range):
    """
    How much the filler: "Chroma Pack" can give chroma at maximum. If you have Shopsanity, i suggest to have a high range of chroma pack.
    """
    internal_name = "max_chroma_pack"
    display_name = "Max Chroma Pack"
    range_start = 0
    range_end = 100_000
    default = 60_000


#############################
########## SHOPS ############
#############################

class Shopsanity(Toggle):
    """
    Add shop items to location pool.
    """
    internal_name = "shopsanity"
    display_name = "Shop Sanity"
    default = 1

class LocationPerShop(Range):
    """
    How many locations are in each shop. Does nothing if Shopsanity is disabled.
    """
    internal_name = "location_per_shop"
    display_name = "Location Per Shop"
    range_start = 0
    range_end = 8
    default = 4

class FightingMerchant(Toggle):
    """
    If enabled, fighting merchant gives a check. Otherwise it will unlock extra items in shop like in vanilla.
    Also, if enabled, you need to find your merchant unlock in the pool to unlock extra items in shop
    """
    internal_name = "fighting_merchant"
    display_name = "Fighting Merchant"
    default = 1

class ExtraLocationPerShop(Range):
    """
    How many locations are in each extra shop (when fighting/having the extra shop item).
    """
    internal_name = "extra_location_per_shop"
    display_name = "Extra Location Per Shop"
    range_start = 0
    range_end = 8
    default = 4

class MinPriceShop(Range):
    """
    How much the price of location shop is at minimum
    """
    internal_name = "min_price_shop"
    display_name = "Minimum Price Shop"
    range_start = 0
    range_end = 100_000
    default = 1_000

class MaxPriceShop(Range):
    """
    How much the price of location shop is at maximum. If it's below the minimum, the max price will be equals to the minimum price
    """
    internal_name = "max_price_shop"
    display_name = "Maximum Price Shop"
    range_start = 0
    range_end = 100_000
    default = 10_000

class ShowShopItems(Toggle):
    """
    Show clearly what the item in shop location is (progressive, item for which player).
    Extra shop locations are hidden until your have the corresponding item to unlock them.
    """
    internal_name = "show_shop_items"
    display_name = "Show Shop Items"
    default = 1

class CreateHintAutomaticallyShop(Toggle):
    """
    Create a hint for shop items. If the Show shop items is disabled, it will also create hint.
    To create hint for extra shop locations, it's an another option
    """
    internal_name = "create_hint"
    display_name = "Create Hint Automatically"
    default = 1

class CreateHintAutomaticallyExtraShop(Toggle):
    """
    Create a hint for extra shop items. Can be useful to know what's behind them
    """
    internal_name = "create_hint_extra"
    display_name = "Create Hint Automatically for Extra items"
    default = 1

class ClairObscurStartInventory(StartInventory):
    """
    Start with these items
    """

@dataclass
class ClairObscurOptions(PerGameCommonOptions):
    goal: Goal
    char_shuffle: ShuffleCharacters
    shuffle_free_aim: ShuffleFreeAim
    exclude_endgame_locations: ExcludeEndgameLocations
    exclude_endless_tower: ExcludeEndlessTower
    exclude_superbosses: ExcludeSuperbosses
    gestral_shuffle: ShuffleLostGestrals
    starting_char: StartingCharacter
    gear_scaling: GearScaling
    max_equip_level: MaxEquipLevel
    custom_max_equip_level: CustomMaxEquipLevel
    area_logic: AreaLogic
    trap_chance: TrapChance

    # Chroma pack
    chroma_pack_type: ChromaPackType
    min_chroma_pack: MinChromaPack
    max_chroma_pack: MaxChromaPack

    # Shops
    shopsanity: Shopsanity
    location_per_shop: LocationPerShop
    fighting_merchant: FightingMerchant
    extra_location_per_shop: ExtraLocationPerShop
    min_price_shop: MinPriceShop
    max_price_shop: MaxPriceShop
    show_shop_items: ShowShopItems
    create_hint: CreateHintAutomaticallyShop
    create_hint_extra: CreateHintAutomaticallyExtraShop


    # AP base
    start_inventory: ClairObscurStartInventory

OPTIONS_GROUP = [
    OptionGroup(
        "Shop", [
            Shopsanity,
            LocationPerShop,
            FightingMerchant,
            ExtraLocationPerShop,
            MinPriceShop,
            MaxPriceShop,
            ShowShopItems,
            CreateHintAutomaticallyShop,
            CreateHintAutomaticallyExtraShop,
        ]),
    OptionGroup(
        "Item & Location Options", [
            ClairObscurStartInventory,
        ]),
]