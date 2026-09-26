"""
Integrity checks on the shared json files

No multiworld is built here so these are fast. They cover the invariants the world code assumes
without checking, and the data/ folder is mirrored on the client side, so a break caught here is a
break caught for both repos
"""
import unittest
from collections import Counter

from ..Data import load_json_data
from ..Items import create_item_groups
from ..Locations import create_location_groups
from ..Rules import GOAL_REGIONS


class TestDataIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.items = load_json_data("items.json")
        cls.locations = load_json_data("locations.json")
        cls.regions = load_json_data("regions.json")
        cls.connections = load_json_data("connections.json")
        cls.shops = load_json_data("shops.json")

        cls.item_names = {item["name"] for item in cls.items}
        cls.location_names = {loc["name"] for loc in cls.locations}
        cls.region_names = {region["region_name"] for region in cls.regions}

        cls.claimed_by = {name: r["region_name"] for r in cls.regions for name in r["locations"]}

    @staticmethod
    def duplicates(names) -> list:
        return sorted(name for name, count in Counter(names).items() if count > 1)

    def test_item_names_are_unique(self) -> None:
        self.assertEqual([], self.duplicates(item["name"] for item in self.items))

    def test_region_names_are_unique(self) -> None:
        self.assertEqual([], self.duplicates(region["region_name"] for region in self.regions))

    def test_duplicate_locations_are_all_marked_multiple(self) -> None:
        for name in self.duplicates(loc["name"] for loc in self.locations):
            entries = [loc for loc in self.locations if loc["name"] == name]
            with self.subTest(location=name):
                self.assertTrue(all(entry.get("multiple") for entry in entries),
                                f"{name} appears {len(entries)} times but is not marked multiple")

    def test_regions_only_claim_known_locations(self) -> None:
        unknown = sorted(set(self.claimed_by) - self.location_names)
        self.assertEqual([], unknown)

    def test_every_location_is_claimed_exactly_once(self) -> None:
        claimed = [name for region in self.regions for name in region["locations"]]
        self.assertEqual([], self.duplicates(claimed), "location claimed by two regions")
        self.assertEqual(set(), self.location_names - set(claimed), "location claimed by no region")

    def test_connections_link_known_regions(self) -> None:
        known = self.region_names | {"Menu"}
        for conn in self.connections:
            with self.subTest(connection=f"{conn['from']} -> {conn['to']}"):
                self.assertIn(conn["from"], known)
                self.assertIn(conn["to"], known)

    def test_conditions_reference_known_items(self) -> None:
        referenced = set()
        for conn in self.connections:
            referenced |= set(conn["condition"] or {})
        for loc in self.locations:
            referenced |= set(loc["condition"] or {})
        self.assertEqual(set(), referenced - self.item_names)

    def test_shops_are_consistent(self) -> None:
        for shop in self.shops:
            with self.subTest(shop=shop["name"]):
                self.assertIn(shop["region"], self.region_names)
                self.assertIn("unlock_item", shop, "missing key, Data.py reads it without a default")
                if shop.get("has_fight"):
                    self.assertIsNotNone(shop["unlock_item"], "a fight shop needs an unlock item")
                    self.assertIn(shop["unlock_item"], self.item_names)

    def test_goal_regions_exist(self) -> None:
        for goal_value, region_name in GOAL_REGIONS.items():
            with self.subTest(goal=goal_value):
                self.assertIn(region_name, self.region_names)

    def test_classifications_are_known(self) -> None:
        self.assertEqual(set(), {item["progressive"] for item in self.items} - set(range(6)))

    def test_every_item_type_has_a_group(self) -> None:
        from ..Data import data
        self.assertEqual(set(), {item.type for item in data.items.values()} - set(create_item_groups(data.items)))

    def test_every_location_type_has_a_group(self) -> None:
        from ..Data import data
        types = {loc.type for loc in data.locations.values()}
        self.assertEqual(set(), types - set(create_location_groups(data.locations)))