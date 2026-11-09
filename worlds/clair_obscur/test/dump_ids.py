"""
Writes the id snapshot that the regression test compares against (and could be use for poptracker *wink yezz*)

Never run it to make a failing test pass. If an id moved, it's a bug probably
"""
import json
from pathlib import Path

from ..items import create_item_name_to_ap_id
from ..locations import create_location_name_to_ap_id

SNAPSHOT_DIR = Path(__file__).parent / "data"


def write(name: str, mapping: dict[str, int]) -> None:
    SNAPSHOT_DIR.mkdir(exist_ok=True)
    target = SNAPSHOT_DIR / name
    with target.open("w", encoding="utf-8") as handle:
        json.dump(mapping, handle, indent=2, sort_keys=True, ensure_ascii=False)
    print(f"wrote {target} ({len(mapping)} entries)")


if __name__ == "__main__":
    write("item_ids.json", create_item_name_to_ap_id())
    write("location_ids.json", create_location_name_to_ap_id())