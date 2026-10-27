BASE_OFFSET = 330000
LOCATION_OFFSET = 3300

# Deepest region level in regions.json and the highest gear level the game goes to
MAX_GEAR_LEVEL = 33

# Id space reserved per shop has to stay in sync with the ranges of LocationPerShop and ExtraLocationPerShop
MAX_SHOP_SLOT = 8

# Shops whose slots are always EXCLUDED
# Noco : can disappear after finishing FW
EXCLUDED_SHOPS = frozenset({"Noco"})

# goal name -> region that has to be reachable to win
GOAL_REGIONS = {
    "paintress": "The Monolith",
    "curator": "Lumiere",
    "painted_love": "Endless Tower Stage 11",
    "simon": "Renoir's Drafts",
    "clea": "Flying Manor",
    "osquio": "Verso's Drafts"
}

# A goal that stops before the endgame caps what gear level the pool can hold
# The goals not listed here go up to MAX_GEAR_LEVEL (which is 33)
GOAL_LEVEL_CAPS = {
    "paintress": 15,
    "curator": 16,
    "clea": 28,
}