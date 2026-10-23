from typing import Any

from Fill import distribute_items_restrictive
from worlds.AutoWorld import call_all
from . import ClairObscurTestBase
from ..game_data import data


class SlotDataAssertions(ClairObscurTestBase):
    def build_slot_data(self) -> dict:
        distribute_items_restrictive(self.multiworld)
        call_all(self.multiworld, "post_fill")
        return self.world.fill_slot_data()

    def test_totals_match_the_item_groups(self) -> None:
        slot_data = self.build_slot_data()
        self.assertEqual(len(self.world.item_name_groups["Picto"]), slot_data["totals"]["pictos"])
        self.assertEqual(len(self.world.item_name_groups["Weapon"]), slot_data["totals"]["weapons"])


class TestSpherePlacement(SlotDataAssertions, ClairObscurTestBase):
    options = {"gear_scaling": "sphere_placement"}

    def test_every_picto_appears_once_in_sphere_order(self) -> None:
        slot_data: dict[str, Any] = self.build_slot_data()
        picto_ids = slot_data["pictos"]

        self.assertEqual(len(picto_ids), len(set(picto_ids)), "a picto id shows up twice")
        expected = {self.world.item_name_to_id[name] for name in self.world.item_name_groups["Picto"]}
        self.assertEqual(expected, set(picto_ids), "some pictos never made it into the sphere list")


class TestBalancedRandom(SlotDataAssertions, ClairObscurTestBase):
    options = {"gear_scaling": "balanced_random"}

    def test_lists_are_a_shuffle_of_every_id(self) -> None:
        slot_data = self.build_slot_data()
        for group, key in [("Picto", "pictos"), ("Weapon", "weapons")]:
            with self.subTest(group=group):
                expected = {self.world.item_name_to_id[name] for name in self.world.item_name_groups[group]}
                self.assertEqual(expected, set(slot_data[key]))
                self.assertEqual(len(expected), len(slot_data[key]))


class TestOrderReceivedSendsNoList(SlotDataAssertions, ClairObscurTestBase):
    options = {"gear_scaling": "order_received"}

    def test_client_side_scaling_sends_nothing(self) -> None:
        slot_data = self.build_slot_data()
        self.assertNotIn("pictos", slot_data)
        self.assertNotIn("weapons", slot_data)


class TestMaxGearLevel(SlotDataAssertions, ClairObscurTestBase):
    options = {"max_equip_level": "custom", "custom_max_equip_level": 12}

    def test_custom_level_is_forwarded(self) -> None:
        self.assertEqual(12, self.build_slot_data()["max_gear_level"])


class TestMaxGearLevelFollowsTheGoal(SlotDataAssertions, ClairObscurTestBase):
    options = {"max_equip_level": "highest_included_location", "goal": "paintress",
               "exclude_endgame_locations": "excluded"}

    def test_highest_included_location_is_used(self) -> None:
        self.assertEqual(15, self.build_slot_data()["max_gear_level"])


class TestShopPrices(SlotDataAssertions, ClairObscurTestBase):
    options = {"shopsanity": True, "location_per_shop": 3, "extra_location_per_shop": 2,
               "min_price_shop": 1000, "max_price_shop": 5000}

    def test_one_price_per_shop_slot_inside_the_range(self) -> None:
        shops = self.build_slot_data()["shops"]
        self.assertEqual(set(data.shops), set(shops))
        for shop_name, shop in data.shops.items():
            with self.subTest(shop=shop_name):
                entry = shops[shop_name]
                self.assertEqual(3, len(entry["prices"]))
                self.assertEqual(2 if shop.has_fight else 0, len(entry["extra_prices"]))
                for price in entry["prices"] + entry["extra_prices"]:
                    self.assertGreaterEqual(price, 1000)
                    self.assertLessEqual(price, 5000)


class TestInvertedPriceRange(SlotDataAssertions, ClairObscurTestBase):
    options = {"shopsanity": True, "location_per_shop": 2, "extra_location_per_shop": 0,
               "min_price_shop": 5000, "max_price_shop": 1000}

    def test_every_price_falls_back_to_the_minimum(self) -> None:
        shops = self.build_slot_data()["shops"]
        for shop_name, entry in shops.items():
            with self.subTest(shop=shop_name):
                self.assertEqual([5000] * 2, entry["prices"])


class TestChromaFixedRange(SlotDataAssertions, ClairObscurTestBase):
    options = {"chroma_pack_type": "random_fixed_range", "min_chroma_pack": 1000, "max_chroma_pack": 2000}

    def test_a_single_value_is_rolled_and_sent(self) -> None:
        chroma = self.build_slot_data()["chroma"]
        self.assertGreaterEqual(chroma, 1000)
        self.assertLessEqual(chroma, 2000)


class TestChromaClientRange(SlotDataAssertions, ClairObscurTestBase):
    options = {"chroma_pack_type": "random_range", "min_chroma_pack": 1000, "max_chroma_pack": 2000}

    def test_the_client_rolls_it_so_nothing_is_sent(self) -> None:
        self.assertNotIn("chroma", self.build_slot_data())

class TestConsumableDefaults(SlotDataAssertions, ClairObscurTestBase):
    options = {}

    def test_untouched_options_give_the_old_amount(self) -> None:
        consumables = self.build_slot_data()["consumables"]
        self.assertEqual(5, len(consumables))
        for name, (low, high) in consumables.items():
            with self.subTest(item=name):
                self.assertEqual([5, 5], [low, high])


class TestConsumablePartialOverride(SlotDataAssertions, ClairObscurTestBase):
    options = {
        "consumable_roll_type": "random_range",
        "consumable_min": {"Colour of Lumina": 10},
        "consumable_max": {"Colour of Lumina": 40},
    }

    def test_only_the_named_item_moved(self) -> None:
        consumables = self.build_slot_data()["consumables"]
        self.assertEqual([10, 40], consumables["Colour of Lumina"])
        self.assertEqual([5, 5], consumables["Chroma Catalyst"])


class TestConsumableInvertedRange(SlotDataAssertions, ClairObscurTestBase):
    options = {
        "consumable_roll_type": "random_range",
        "consumable_min": {"Chroma Catalyst": 20},
        "consumable_max": {"Chroma Catalyst": 3},
    }

    def test_max_under_min_is_raised(self) -> None:
        self.assertEqual([20, 20], self.build_slot_data()["consumables"]["Chroma Catalyst"])


class TestConsumableFixedRoll(SlotDataAssertions, ClairObscurTestBase):
    options = {
        "consumable_roll_type": "random_fixed_range",
        "consumable_min": {"Colour of Lumina": 1},
        "consumable_max": {"Colour of Lumina": 50},
    }

    def test_a_fixed_roll_is_a_range_of_one(self) -> None:
        low, high = self.build_slot_data()["consumables"]["Colour of Lumina"]
        self.assertEqual(low, high)
        self.assertGreaterEqual(low, 1)
        self.assertLessEqual(high, 50)