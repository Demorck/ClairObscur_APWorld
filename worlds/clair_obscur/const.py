BASE_OFFSET = 330000
LOCATION_OFFSET = 3300

# Deepest region level in regions.json and the highest gear level the game goes to
MAX_GEAR_LEVEL = 33

# Id space reserved per shop has to stay in sync with the ranges of LocationPerShop and ExtraLocationPerShop
MAX_SHOP_SLOT = 8

# Shop get their own range so adding a location never shifts ID. (unless if we have more than 10k location which is huge)
SHOP_ID_BASE = 10_000

# Reserved even if shop don't have fight / extra items
SHOP_ID_RESERVED = MAX_SHOP_SLOT * 2 + 1

# Shops whose slots are always EXCLUDED
# Noco : can disappear after finishing FW
EXCLUDED_SHOPS = frozenset({"Noco"})