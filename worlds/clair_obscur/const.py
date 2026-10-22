BASE_OFFSET = 330000
LOCATION_OFFSET = 3300

# Deepest region level in regions.json and the highest gear level the game goes to
MAX_GEAR_LEVEL = 33

# Id space reserved per shop has to stay in sync with the ranges of LocationPerShop and ExtraLocationPerShop
MAX_SHOP_SLOT = 8

# Shops whose slots are always EXCLUDED
# Noco : can disappear after finishing FW
EXCLUDED_SHOPS = frozenset({"Noco"})