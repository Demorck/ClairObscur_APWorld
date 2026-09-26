from BaseClasses import CollectionState
from test.bases import WorldTestBase
from typing import TYPE_CHECKING

class ClairObscurTestBase(WorldTestBase):
    """
    Shared base for every preset test
    """

    game = "Clair Obscur Expedition 33"
    player = 1

    def empty_state(self) -> CollectionState:
        return CollectionState(self.multiworld)

    def state_without(self, item_name: str) -> CollectionState:
        state = self.empty_state()
        self.collect_all_but(item_name, state)
        return state

    def collect_all_but_pictos(self, state: CollectionState) -> None:
        picto_names = self.world.item_name_groups["Picto"]
        for item in self.multiworld.get_items():
            if item.name not in picto_names:
                state.collect(item)

    def collect_pictos(self, amount: int, state: CollectionState) -> None:
        picto_names = self.world.item_name_groups["Picto"]
        collected = 0
        for item in self.multiworld.itempool:
            if collected >= amount:
                break
            if item.name in picto_names:
                state.collect(item)
                collected += 1
        self.assertEqual(amount, collected, f"only {collected} pictos available, needed {amount}")


if TYPE_CHECKING:
    MixinBase = ClairObscurTestBase
else:
    MixinBase = object