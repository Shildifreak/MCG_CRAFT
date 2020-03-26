from resources import *
from voxelengine.modules.observableCollections import ObservableDict

@register_block("CHEST")
class ChestBlock(Block):
    def activated(self,character,face):
        """something like placing block depending on direction character is looking"""
        # open inventory
        character.foreign_inventory = self["inventory"]
        character["open_inventory"] = True

@register_item("CHEST")
class ChestItem(Item):
    def block_version_on_place(self,character,blockpos,face):
        block_id = self.item["id"]
        r = int((character["rotation"][0] + 45) // 90) % 4
        inventory = ObservableDict()
        for i in range(28):
            inventory[i] = {"id":"AIR"}
        return {"id":block_id,"rotation":r,"inventory":inventory}
