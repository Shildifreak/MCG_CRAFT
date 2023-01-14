from resources import *
from voxelengine.modules.observableCollections import ObservableDict
import random

@register_item("Muenzen")
@register_item("Scheine")
class notPlacable(Item):
    def use_on_block(self,character,blockpos,face):
        """whatever this item should do when click on a block... default is to place a block with same id"""
        return self.use_on_air(character)

class Kreditkarteninventar(ObservableDict):
    def may_contain(self, item):
        if item["id"] in ("Muenzen", "Scheine", "AIR"):
            return True
        else:
            return False

@register_item("Kredidtkarte")
class Kredidtkarte(notPlacable):
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
