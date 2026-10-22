import pkgutil
from collections import defaultdict
from typing import NamedTuple, Any

from orjson import orjson

from BaseClasses import ItemClassification


class ClairObscurItemData(NamedTuple):
    name: str
    item_id: int
    classification: ItemClassification
    type: str

class ClairObscurLocationData(NamedTuple):
    name: str
    region: str
    default_item: str
    condition: dict[str, int]
    type: str
    pictos_level: int
    multiple: bool

class ClairObscurShopData(NamedTuple):
    name: str
    region: str
    has_fight: bool
    unlock_item: str | None


class ClairObscurRegionData:
    name: str
    locations: list[str]
    pictos_level: int

    def __init__(self, name: str, pictos: int):
        self.name = name
        self.locations = []
        self.pictos_level = pictos if pictos is not None else 1

class ClairObscurRegionConnection:
    origin_region: str
    destination_region: str
    condition: dict[str, int]

    def __init__(self, cond: dict[str, int] | None, origin: str, destination: str):
        self.origin_region = origin
        self.destination_region = destination
        self.condition = cond if cond is not None else {}

class ClairObscurData:
    items: dict[int, ClairObscurItemData]
    locations: dict[str, ClairObscurLocationData]
    regions: dict[str, ClairObscurRegionData]
    shops: dict[str, ClairObscurShopData]
    shops_by_region: dict[str, list[ClairObscurShopData]]
    connections: list[ClairObscurRegionConnection]

    def __init__(self) -> None:
        self.items = {}
        self.locations = {}
        self.regions = {}
        self.shops = {}
        self.shops_by_region = {}
        self.connections = []


def load_json_data(data_name: str) -> list[dict[str, Any]]:
    return orjson.loads(pkgutil.get_data(__name__, "data/" + data_name))


def populate_data_shops() -> dict[str, ClairObscurShopData]:
    shops = {}
    shops_json = load_json_data("shops.json")
    for shop in shops_json:
        shop_name = shop.get("name")
        shop_region = shop.get("region")
        shop_has_fight = shop.get("has_fight", False)
        shop_unlock_item = shop.get("unlock_item")

        new_shop = ClairObscurShopData(
            shop_name,
            shop_region,
            shop_has_fight,
            shop_unlock_item
        )

        shops[shop_name] = new_shop

    return shops


def _init() -> None:
    data.items = populate_data_items()
    data.locations = populate_data_locations()
    data.regions = populate_data_regions()
    data.connections = populate_data_connections()
    data.shops = populate_data_shops()
    data.shops_by_region = group_shops_by_region(data.shops)

def populate_data_locations() -> dict[str, ClairObscurLocationData]:
    locations = {}
    locations_json = load_json_data("locations.json")
    for location in locations_json:
        location_name: str = location["name"]
        location_condition = location["condition"]
        pictos = location["pictos_level"] if location.get("pictos_level") else 1
        multiple = location["multiple"] if location.get("multiple") else False

        new_location = ClairObscurLocationData(
            location_name,
            location["location"],
            location["original_item"],
            location_condition,
            location["type"],
            pictos,
            multiple
        )

        locations[location_name] = new_location

    return locations

def populate_data_items() -> dict[int, ClairObscurItemData]:
    items = {}
    items_json = load_json_data("items.json")
    item_id = 0
    for item in items_json:
        item_name: str = item["name"]
        classification = None
        if item["progressive"] == 0:
            classification = ItemClassification.filler
        elif item["progressive"] == 1:
            classification = ItemClassification.progression
        elif item["progressive"] == 2:
            classification = ItemClassification.useful
        elif item["progressive"] == 3:
            classification = ItemClassification.progression | ItemClassification.skip_balancing
        elif item["progressive"] == 4:
            classification = (ItemClassification.progression | ItemClassification.skip_balancing |
                              ItemClassification.deprioritized)
        elif item["progressive"] == 5:
            classification = ItemClassification.trap
        else:
            raise ValueError(f"Unknown classification '{item['progressive']}' for {item_name}")

        items[item_id] = ClairObscurItemData(
            item_name,
            item_id,
            classification,
            item["type"]
        )

        item_id += 1

    return items

def populate_data_regions() -> dict[str, ClairObscurRegionData]:
    regions = {}
    claimed_locations = set()
    regions_json = load_json_data("regions.json")
    for region in regions_json:
        region_name = region["region_name"]
        region_level = region["level"]
        current_region_data = ClairObscurRegionData(
            region_name,
            region_level
        )

        for location_name in region["locations"]:
            if location_name in claimed_locations:
                raise AssertionError(f"Location {location_name} is claimed by two regions")

            current_region_data.locations.append(location_name)
            claimed_locations.add(location_name)

        current_region_data.locations.sort()

        regions[region_name] = current_region_data

    return regions

def populate_data_connections() -> list[ClairObscurRegionConnection]:
    region_connections = []
    conns_json = load_json_data("connections.json")
    for conn in conns_json:
        conn_from = conn["from"]
        conn_to = conn["to"]
        conn_condition = conn["condition"]

        new_connection = ClairObscurRegionConnection(
            conn_condition,
            conn_from,
            conn_to
        )

        region_connections.append(new_connection)

    return region_connections

def group_shops_by_region(shops: dict[str, ClairObscurShopData]) -> dict[str, list[ClairObscurShopData]]:
    """
    Group the shops by the region where is the shop

    Args:
        shops: Every shop keyed by name

    Returns:
        Shop of each region
    """
    by_region = defaultdict(list)
    for shop in shops.values():
        by_region[shop.region].append(shop)

    return dict(by_region)

data = ClairObscurData()
_init()