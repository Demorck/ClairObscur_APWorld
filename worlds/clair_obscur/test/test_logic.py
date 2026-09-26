from ..Data import data
from . import ClairObscurTestBase


class TestDataDrivenConditions(ClairObscurTestBase):
    options = {
        "goal": "simon",
        "exclude_endgame_locations": "included",
        "exclude_endless_tower": "included",
        "exclude_superbosses": "included",
        "gestral_shuffle": True,
        "shuffle_free_aim": True,
        "shopsanity": False,
    }

    def test_every_connection_condition_gates_its_entrance(self) -> None:
        for conn in data.connections:
            if not conn.condition:
                continue
            name = f"{conn.origin_region} -> {conn.destination_region}"
            entrance = self.multiworld.get_entrance(name, self.player)
            for item_name in conn.condition:
                with self.subTest(entrance=name, without=item_name):
                    self.assertFalse(entrance.access_rule(self.state_without(item_name)),
                                     f"{name} opens without {item_name}")

    def test_every_connection_condition_is_enough(self) -> None:
        for conn in data.connections:
            name = f"{conn.origin_region} -> {conn.destination_region}"
            entrance = self.multiworld.get_entrance(name, self.player)
            with self.subTest(entrance=name):
                self.assertTrue(entrance.access_rule(self.multiworld.get_all_state()))

    def test_every_location_condition_gates_its_location(self) -> None:
        for location_name, location_data in data.locations.items():
            if not location_data.condition:
                continue
            location = self.multiworld.get_location(location_name, self.player)
            for item_name in location_data.condition:
                with self.subTest(location=location_name, without=item_name):
                    self.assertFalse(location.access_rule(self.state_without(item_name)),
                                     f"{location_name} opens without {item_name}")


class TestPictoGating(ClairObscurTestBase):
    options = {"goal": "simon", "exclude_endgame_locations": "included"}

    def test_convert_pictos_formula(self) -> None:
        # scale by order received, one region level costs 5.8 pictos rounded up
        self.assertEqual(0, self.world.convert_pictos(1))
        self.assertEqual(6, self.world.convert_pictos(2))
        self.assertEqual(186, self.world.convert_pictos(33))

    def test_pool_holds_enough_pictos_for_the_deepest_region(self) -> None:
        deepest = max(region.pictos_level for region in data.regions.values())
        available = len(self.world.item_name_groups["Picto"])
        self.assertGreaterEqual(available, self.world.convert_pictos(deepest),
                                "not enough pictos in the pool to ever reach the deepest region")

    def test_picto_threshold_is_exact(self) -> None:
        one_per_level = {}
        for region_name, region_data in data.regions.items():
            if region_data.pictos_level > 1:
                one_per_level.setdefault(region_data.pictos_level, region_name)

        for level, region_name in sorted(one_per_level.items()):
            required = self.world.convert_pictos(level)
            for entrance in self.multiworld.get_region(region_name, self.player).entrances:
                with self.subTest(region=region_name, level=level, pictos=required - 1):
                    state = self.empty_state()
                    self.collect_all_but_pictos(state)
                    self.collect_pictos(required - 1, state)
                    self.assertFalse(entrance.access_rule(state),
                                     f"{entrance.name} opens with only {required - 1} pictos")

                with self.subTest(region=region_name, level=level, pictos=required):
                    state = self.empty_state()
                    self.collect_all_but_pictos(state)
                    self.collect_pictos(required, state)
                    self.assertTrue(entrance.access_rule(state),
                                    f"{entrance.name} stays shut with {required} pictos")


class TestCharacterRules(ClairObscurTestBase):
    options = {"char_shuffle": True, "starting_char": "gustave", "goal": "simon",
               "exclude_endgame_locations": "included"}

    def test_only_the_starting_character_is_precollected(self) -> None:
        chars = self.world.item_name_groups["Character"]
        precollected = {item.name for item in self.multiworld.precollected_items[self.player]}
        self.assertEqual({"Gustave"}, precollected & chars)

    def test_the_other_five_characters_are_in_the_pool(self) -> None:
        chars = self.world.item_name_groups["Character"]
        in_pool = [item.name for item in self.multiworld.itempool if item.name in chars]
        self.assertCountEqual(["Maelle", "Lune", "Sciel", "Monoco", "Verso"], in_pool)

    def test_golgra_needs_monoco(self) -> None:
        self.assertAccessDependency(["Sacred River: Golgra"], [["Monoco"]], only_check_listed=True)

    def test_sky_branches_need_their_character(self) -> None:
        for entrance_name, character in [("WM: Sky -> The Reacher", "Maelle"),
                                         ("WM: Sky -> Sirene's Dress", "Sciel")]:
            with self.subTest(entrance=entrance_name):
                entrance = self.multiworld.get_entrance(entrance_name, self.player)
                self.assertFalse(entrance.access_rule(self.state_without(character)))

    def test_chosen_path_needs_the_whole_party(self) -> None:
        entrance = self.multiworld.get_entrance("WM: Sky -> The Chosen Path", self.player)
        for character in ["Lune", "Sciel", "Monoco", "Maelle", "Verso"]:
            with self.subTest(without=character):
                self.assertFalse(entrance.access_rule(self.state_without(character)))

    def test_sea_crossings_need_a_party(self) -> None:
        # three characters for the first crossing, four for the second
        for entrance_name, needed in [("WM: First Continent South -> WM: South Sea", 3),
                                      ("WM: South Sea -> WM: North Sea", 4)]:
            entrance = self.multiworld.get_entrance(entrance_name, self.player)
            chars = ["Maelle", "Lune", "Sciel", "Monoco", "Verso"]
            with self.subTest(entrance=entrance_name):
                state = self.empty_state()
                self.collect_all_but(chars, state)
                # Gustave is precollected so needed - 1 more are required
                self.collect_by_name(chars[:needed - 2])
                self.assertFalse(entrance.access_rule(state))


class TestAreaLogicNormal(ClairObscurTestBase):
    options = {"area_logic": "normal", "goal": "simon", "exclude_endgame_locations": "included"}

    def test_first_crossing_needs_every_act_one_area(self) -> None:
        entrance = self.multiworld.get_entrance("WM: First Continent South -> WM: South Sea", self.player)
        for area in ["Area - Flying Waters", "Area - Ancient Sanctuary",
                     "Area - Yellow Harvest", "Area - Stone Wave Cliffs"]:
            with self.subTest(without=area):
                self.assertFalse(entrance.access_rule(self.state_without(area)))


class TestAreaLogicHardIsLooser(ClairObscurTestBase):
    options = {"area_logic": "hard", "goal": "simon", "exclude_endgame_locations": "included"}

    def test_first_crossing_needs_only_half_the_areas(self) -> None:
        # hard asks for 4 // 2 areas, so dropping a single one must not close the edge
        entrance = self.multiworld.get_entrance("WM: First Continent South -> WM: South Sea", self.player)
        self.assertTrue(entrance.access_rule(self.state_without("Area - Flying Waters")))