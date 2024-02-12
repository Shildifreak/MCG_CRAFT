from resources import *
from voxelengine.modules.observableCollections import ObservableDict
import random



class CraftingInventar(ObservableDict):
    SLOT_1 = 3
    SLOT_2 = 4
    RECIPIES = {}
    def __init__(self):
        super().__init__({self.SLOT_1:{"id":"AIR"}, self.SLOT_2:{"id":"AIR"}},)
        
    def on_close(self):
        incredient_1 = self[self.SLOT_1]
        incredient_2 = self[self.SLOT_2]
        incredient_names = frozenset({incredient_1["id"],incredient_2["id"]}) - {"AIR"}
        result = self.RECIPIES.get(incredient_names, None)
        if result:
            result_item = {"id":result}
            crafting_item = self.parent
            player_inventory = crafting_item.parent
            player = player_inventory.parent

            ItemFactory(incredient_1).decrease_count()
            ItemFactory(incredient_2).decrease_count()
            ItemFactory(crafting_item).decrease_count()
            player.pickup_item(result_item)
        elif incredient_names:
            print("No recipe for incredients:", incredient_names)

class StringCraftingInventar(CraftingInventar):
    RECIPIES = {
        frozenset({"Stick3"}) : "Bow",
        frozenset({"Stick3", "Hook"}) : "Fishing_Rod",
        frozenset({"Stick1", "STONE"}) : "Axe",
    }

class GlueCraftingInventar(CraftingInventar):
    RECIPIES = {
        frozenset({"Stick1", "STONE"}) : "Axe",
    }

@register_item("String")
class Kredidtkarte(UnplacableItem):
    def use_on_air(self, character):
        # open inventory
        if not "inventory" in self.item.keys():
            self.item["inventory"] = StringCraftingInventar()
        character.foreign_inventory = self.item["inventory"]
        character["open_inventory"] = True
    
@register_item("Glue")
class Glue(UnplacableItem):
    def use_on_air(self, character):
        # open inventory
        if not "inventory" in self.item.keys():
            self.item["inventory"] = GlueCraftingInventar()
        character.foreign_inventory = self.item["inventory"]
        character["open_inventory"] = True
