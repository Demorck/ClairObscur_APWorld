"""
Basically just test some presets if every item is accessible and goal reachable
"""
from . import ClairObscurTestBase


class TestGoalPaintress(ClairObscurTestBase):
    options = {"goal": "paintress"}


class TestGoalClea(ClairObscurTestBase):
    options = {"goal": "clea"}


class TestGoalSimonEverythingIncluded(ClairObscurTestBase):
    options = {
        "goal": "simon",
        "exclude_endgame_locations": "included",
        "exclude_endless_tower": "included",
        "exclude_superbosses": "included",
    }


class TestFillerExclusionMode(ClairObscurTestBase):
    options = {
        "exclude_endgame_locations": "filler",
        "exclude_endless_tower": "filler",
        "exclude_superbosses": "filler",
    }


class TestFullShuffle(ClairObscurTestBase):
    options = {
        "char_shuffle": True,
        "starting_char": "maelle",
        "gestral_shuffle": True,
        "shuffle_free_aim": True,
    }


class TestNoShopsanity(ClairObscurTestBase):
    options = {"shopsanity": False}


class TestShopsWithoutFightingMerchant(ClairObscurTestBase):
    options = {"shopsanity": True, "fighting_merchant": False}


class TestShopsMinimalSlots(ClairObscurTestBase):
    options = {
        "goal": "paintress",
        "shopsanity": True,
        "location_per_shop": 0,
        "extra_location_per_shop": 0,
    }


class TestSpherePlacementScaling(ClairObscurTestBase):
    options = {"gear_scaling": "sphere_placement"}


class TestBalancedRandomScaling(ClairObscurTestBase):
    options = {"gear_scaling": "balanced_random"}


class TestAreaLogicHard(ClairObscurTestBase):
    options = {"area_logic": "hard"}


class TestAreaLogicNone(ClairObscurTestBase):
    options = {"area_logic": "no_logic"}


class TestTrapsEverywhere(ClairObscurTestBase):
    options = {"trap_chance": 100}


class TestCustomMaxEquipLevel(ClairObscurTestBase):
    options = {"max_equip_level": "custom", "custom_max_equip_level": 12}