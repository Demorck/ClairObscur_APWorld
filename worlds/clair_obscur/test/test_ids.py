"""
Ids must never move

Appending is fine, renaming is fine once declared below. Moving an existing entry is not
"""
import json
import unittest
from pathlib import Path

from ..items import create_item_name_to_ap_id
from ..locations import create_location_name_to_ap_id

SNAPSHOT_DIR = Path(__file__).parent / "data"

# old name -> new name
RENAMED_ITEMS: dict[str, str] = {
    # 0.5.0 : amount moved from the name to options
    "Chroma Catalyst (5)": "Chroma Catalyst",
    "Polished Chroma Catalyst (5)": "Polished Chroma Catalyst",
    "Resplendent Chroma Catalyst (5)": "Resplendent Chroma Catalyst",
    "Grandiose Chroma Catalyst (5)": "Grandiose Chroma Catalyst",
    "Colour of Lumina (5)": "Colour of Lumina",
}

RENAMED_LOCATIONS: dict[str, str] = {
}


class TestIdsNeverMove(unittest.TestCase):
    def check(self, snapshot_name: str, current: dict[str, int], renames: dict[str, str]) -> None:
        with (SNAPSHOT_DIR / snapshot_name).open(encoding="utf-8") as handle:
            snapshot: dict[str, int] = json.load(handle)

        for old_name, expected_id in snapshot.items():
            name = renames.get(old_name, old_name)
            with self.subTest(entry=old_name):
                self.assertIn(name, current,
                              f"{old_name} is gone. If you renamed it, declare it in the renames dict")
                self.assertEqual(expected_id, current[name],
                                 f"{name} moved from {expected_id} to {current[name]}, an entry was "
                                 f"inserted instead of appended")

    def test_item_ids(self) -> None:
        self.check("item_ids.json", create_item_name_to_ap_id(), RENAMED_ITEMS)

    def test_location_ids(self) -> None:
        self.check("location_ids.json", create_location_name_to_ap_id(), RENAMED_LOCATIONS)