from dataclasses import dataclass
from Options import Choice, PerGameCommonOptions, StartInventory, OptionGroup, Toggle, Range, OptionCounter, OptionSet
from worlds.clair_obscur.const import GOAL_REGIONS

CONSUMABLE_ITEMS = frozenset({
    "Chroma Catalyst",
    "Polished Chroma Catalyst",
    "Resplendent Chroma Catalyst",
    "Grandiose Chroma Catalyst",
    "Colour of Lumina",
})

DEFAULT_CONSUMABLE_AMOUNT = 5

# How ofter each filer shows up in the rotation that fill the pool
# Could add an option to modify this
FILLER_ITEMS = CONSUMABLE_ITEMS | { "Chroma Pack" }

DEFAULT_FILLER_WEIGHTS = {
    "Chroma Catalyst": 2,
    "Polished Chroma Catalyst": 3,
    "Resplendent Chroma Catalyst": 4,
    "Grandiose Chroma Catalyst": 5,
    "Colour of Lumina": 10,
    "Chroma Pack": 10,
}

class Goal(OptionSet):
    """
    The victory condition for your run. Pick one or several.
    Allowed values: paintress, curator, clea, painted_love, simon
    Leaving it empty rolls one for you.
    Curator is the one in Lumiere Act 3
    """
    display_name = "Goal"
    valid_keys = frozenset(GOAL_REGIONS)
    default = frozenset({"curator"})

class GoalRequirement(Choice):
    """
    Only matters when you picked several goals.
    All: every goal has to be done to win.
    Any: the first one you reach wins, you choose your route in game.
    """
    display_name = "Goal Requirement"
    option_all = 0
    option_any = 1
    default = 0

class ExcludeEndgameLocations(Choice):
    """
    Determines how to handle locations higher level than the set goal, if the goal is Paintress or Curator.
    Excluded: Locations won't be added to the pool.
    Filler: Locations will only contain filler items.
    Included: All locations are included.
    """
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
    display_name = "Exclude Superbosses"
    option_excluded = 0
    option_filler = 1
    option_included = 2
    default = 0

class ShuffleLostGestrals(Toggle):
    """
    Shuffles the lost gestrals into the item pool.
    """
    display_name = "Shuffle Lost Gestrals"

class ShuffleFreeAim(Toggle):
    """
    Shuffles the ability to shoot outside of battle into the pool.
    """
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
    display_name = "Max Equipment Level"
    option_highest_included_location = 0
    option_custom = 1

class CustomMaxEquipLevel(Range):
    """
    What level pictos and weapons received through Archipelago will go up to if Max Equip Level is set to Custom.
    """
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
    display_name = "Chroma pack type"
    option_random_fixed_range = 0
    option_random_range = 1

class MinChromaPack(Range):
    """
    How much the filler: "Chroma Pack" can give chroma at minimum. If you have Shopsanity, i suggest to have a high range of chroma pack.
    """
    display_name = "Min Chroma Pack"
    range_start = 0
    range_end = 100_000
    default = 20_000

class MaxChromaPack(Range):
    """
    How much the filler: "Chroma Pack" can give chroma at maximum. If you have Shopsanity, i suggest to have a high range of chroma pack.
    """
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
    display_name = "Shop Sanity"
    default = 1

class LocationPerShop(Range):
    """
    How many locations are in each shop. Does nothing if Shopsanity is disabled.
    """
    display_name = "Location Per Shop"
    range_start = 0
    range_end = 8
    default = 4

class FightingMerchant(Toggle):
    """
    If enabled, fighting merchant gives a check. Otherwise it will unlock extra items in shop like in vanilla.
    Also, if enabled, you need to find your merchant unlock in the pool to unlock extra items in shop
    """
    display_name = "Fighting Merchant"
    default = 1

class ExtraLocationPerShop(Range):
    """
    How many locations are in each extra shop (when fighting/having the extra shop item).
    """
    display_name = "Extra Location Per Shop"
    range_start = 0
    range_end = 8
    default = 4

class MinPriceShop(Range):
    """
    How much the price of location shop is at minimum
    """
    display_name = "Minimum Price Shop"
    range_start = 0
    range_end = 100_000
    default = 1_000

class MaxPriceShop(Range):
    """
    How much the price of location shop is at maximum. If it's below the minimum, the max price will be equals to the minimum price
    """
    display_name = "Maximum Price Shop"
    range_start = 0
    range_end = 100_000
    default = 10_000

class ShowShopItems(Toggle):
    """
    Show clearly what the item in shop location is (progressive, item for which player).
    Extra shop locations are hidden until your have the corresponding item to unlock them.
    """
    display_name = "Show Shop Items"
    default = 1

#############################
######### FILLERS ###########
#############################

class FillerWeights(OptionCounter):
    """
    How often each filler shows up when the pool needs to be filled
    A key you remove keeps its default and a key set to 0 never shows up at all (if you don't want Colour of lumina...)
    Allowed keys: Chroma Catalyst, Polished Chroma Catalyst, Resplendent Chroma Catalyst,
    Grandiose Chroma Catalyst, Colour of Lumina, Chroma Pack
    """
    display_name = "Filler Weights"
    valid_keys = FILLER_ITEMS
    min = 0
    max = 100
    default = dict(DEFAULT_FILLER_WEIGHTS)

class ConsumableRollType(Choice):
    """
    Random fixed range: one amount is rolled per consumable when the world is generated
    Random range: the client rolls inside the range every time you receive one
    """
    display_name = "Consumable Roll Type"
    option_random_fixed_range = 0
    option_random_range = 1
    default = 0

class ConsumableMin(OptionCounter):
    """
    How much each consumable gives at minimum, default its 5.
    Allowed keys: Chroma Catalyst, Polished Chroma Catalyst, Resplendent Chroma Catalyst,
    Grandiose Chroma Catalyst, Colour of Lumina
    """
    display_name = "Minimum Consumable Amount"
    valid_keys = CONSUMABLE_ITEMS
    min = 1
    max = 999
    default = {name: DEFAULT_CONSUMABLE_AMOUNT for name in sorted(CONSUMABLE_ITEMS)}


class ConsumableMax(OptionCounter):
    """
    How much each consumable gives at maximum, default its also 5
    A value under its matching minimum is raised to it
    """
    display_name = "Maximum Consumable Amount"
    valid_keys = CONSUMABLE_ITEMS
    min = 1
    max = 999
    default = {name: DEFAULT_CONSUMABLE_AMOUNT for name in sorted(CONSUMABLE_ITEMS)}


#############################
###### DEFAULT STUFF ########
#############################

class CreateHintAutomaticallyShop(Toggle):
    """
    Create a hint for shop items. If the Show shop items is disabled, it will also create hint.
    To create hint for extra shop locations, it's an another option
    """
    display_name = "Create Hint Automatically"
    default = 1

class CreateHintAutomaticallyExtraShop(Toggle):
    """
    Create a hint for extra shop items. Can be useful to know what's behind them
    """
    display_name = "Create Hint Automatically for Extra items"
    default = 1

class ClairObscurStartInventory(StartInventory):
    """
    Start with these items
    """

@dataclass
class ClairObscurOptions(PerGameCommonOptions):
    goal: Goal
    goal_requirement: GoalRequirement

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
    filler_weights: FillerWeights

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

    # Consumables
    consumable_roll_type: ConsumableRollType
    consumable_min: ConsumableMin
    consumable_max: ConsumableMax

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
        "Fillers & Consumables", [
            FillerWeights,
            ConsumableRollType,
            ConsumableMin,
            ConsumableMax
        ]),
    OptionGroup(
        "Item & Location Options", [
            ClairObscurStartInventory,
        ]),
]