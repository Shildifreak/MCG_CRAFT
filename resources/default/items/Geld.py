from resources import *
from voxelengine.modules.observableCollections import ObservableDict
import random

@register_item("Muenzen")
@register_item("Scheine")
class Geld(UnplacableItem):
    pass

class Kreditkarteninventar(ObservableDict):
    def may_contain(self, item):
        if item["id"] in ("Muenzen", "Scheine", "AIR"):
            return True
        else:
            return False

@register_item("Kredidtkarte")
class Kredidtkarte(UnplacableItem):
     def use_on_air(self, character):
        # open inventory
        #if not "inventory" in self.item:
        try:
            self.item["inventory"]
        except KeyError:
            self.item["inventory"] = Kreditkarteninventar()
            for i in range(28):
                item_id = random.choices(["AIR","Muenzen","Scheine"],[5,3,2])[0]
                self.item["inventory"][i] = {"id":item_id}

        character.foreign_inventory = self.item["inventory"]
        character["open_inventory"] = True
