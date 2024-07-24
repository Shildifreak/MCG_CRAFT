from resources import *
from voxelengine.modules.observableCollections import ObservableDict
import random

@alias("Muenzen")
@alias("Scheine")
class _Geld(UnplacableItem):
    pass

class Kreditkarteninventar(ObservableDict):
    def __init__(self):
        super().__init__()
        for i in range(28):
            item_id = random.choices(["AIR","Muenzen","Scheine"],[5,3,2])[0]
            self[i] = {"id":item_id}

    def may_contain(self, item):
        if item["id"] in ("Muenzen", "Scheine", "AIR"):
            return True
        else:
            return False


class Kredidtkarte(UnplacableItem):
     def use_on_air(self, character):
        # open inventory
        if not "inventory" in self.item.keys():
            self.item["inventory"] = Kreditkarteninventar()

        character.foreign_inventory = self.item["inventory"]
        character["open_inventory"] = True
