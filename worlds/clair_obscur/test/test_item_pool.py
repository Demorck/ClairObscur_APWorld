from ..Data import data
from . import ClairObscurTestBase, MixinBase


class PoolAssertions(MixinBase):

    def pool_names(self) -> list:
        return [item.name for item in self.multiworld.itempool]

    def test_pool_size_matches_free_locations(self) -> None:
        free = len(self.multiworld.get_unfilled_locations(self.player))
        self.assertEqual(free, len(self.multiworld.itempool))

    def test_journals_never_enter_the_pool(self) -> None:
        journals = self.world.item_name_groups["Journal"]
        self.assertEqual([], [name for name in self.pool_names() if name in journals])


class TestDefaultPool(PoolAssertions, ClairObscurTestBase):
    options = {"goal": "curator"}

    def test_fixed_quantities(self) -> None:
        names = self.pool_names()
        for item_name, expected in [("Progressive Rock", 5), ("Rock Crystal", 3),
                                    ("Perfect Chroma Catalyst", 15), ("Healing Tint Shard", 10)]:
            with self.subTest(item=item_name):
                self.assertEqual(expected, names.count(item_name))

    def test_enough_progressive_rocks_for_the_hardest_condition(self) -> None:
        deepest = max([cond.get("Progressive Rock", 0) for cond in
                       [c.condition for c in data.connections] + [l.condition for l in data.locations.values()]])
        self.assertGreaterEqual(self.pool_names().count("Progressive Rock"), deepest)

    def test_no_traps_when_the_chance_is_zero(self) -> None:
        traps = self.world.item_name_groups["Trap"]
        self.assertEqual([], [name for name in self.pool_names() if name in traps])

    def test_filler_names_get_copies_on_top_of_their_base_one(self) -> None:
        self.assertGreater(self.pool_names().count("Chroma Pack"), 1)

class TestGestralsOff(PoolAssertions, ClairObscurTestBase):
    options = {"gestral_shuffle": False}

    def test_no_gestral_item_and_no_gestral_location(self) -> None:
        self.assertNotIn("Lost Gestral", self.pool_names())
        gestral_locations = [location.name for location in self.multiworld.get_locations(self.player)
                             if data.locations.get(location.name)
                             and data.locations[location.name].type == "Lost Gestral"]
        self.assertEqual([], gestral_locations)


class TestGestralsOn(PoolAssertions, ClairObscurTestBase):
    options = {"gestral_shuffle": True}

    def test_nine_gestrals_are_shuffled(self) -> None:
        self.assertEqual(9, self.pool_names().count("Lost Gestral"))


class TestTrapsEverywhere(PoolAssertions, ClairObscurTestBase):
    options = {"trap_chance": 100}

    def test_every_filler_slot_became_a_trap(self) -> None:
        names = self.pool_names()
        self.assertIn("Feet Trap", names)
        for filler_name in ["Chroma Pack", "Colour of Lumina (5)", "Grandiose Chroma Catalyst (5)"]:
            with self.subTest(item=filler_name):
                self.assertEqual(1, names.count(filler_name), "base copy only, no filler slot")


class TestShopsWithoutFightingMerchant(PoolAssertions, ClairObscurTestBase):
    options = {"shopsanity": True, "fighting_merchant": False}

    def test_unlocks_leave_the_pool_and_get_locked_on_the_fights(self) -> None:
        unlocks = self.world.item_name_groups["Merchant Unlock"]
        self.assertEqual([], [name for name in self.pool_names() if name in unlocks])

        fights = [location for location in self.multiworld.get_locations(self.player)
                  if location.name.endswith(" - Fight")]
        self.assertTrue(fights, "shopsanity is on, there should be fight locations")
        for location in fights:
            with self.subTest(location=location.name):
                self.assertIsNotNone(location.item)
                self.assertIn(location.item.name, unlocks)


class TestExclusionFillerMode(ClairObscurTestBase):
    options = {"exclude_superbosses": "filler", "exclude_endless_tower": "filler",
               "exclude_endgame_locations": "included", "goal": "simon"}

    def test_superbosses_are_marked_excluded(self) -> None:
        from BaseClasses import LocationProgressType
        superbosses = [name for name, loc in data.locations.items() if loc.type == "Superboss"]
        self.assertTrue(superbosses)
        for name in superbosses:
            with self.subTest(location=name):
                location = self.multiworld.get_location(name, self.player)
                self.assertEqual(LocationProgressType.EXCLUDED, location.progress_type)