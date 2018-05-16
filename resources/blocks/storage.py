from mcgcraft import Block, register_block, Item, register_item
from observableCollections import ObservableDict

@register_block("CHEST")
class ChestBlock(Block):
    def activated(self,character,face):
        """something like placing block depending on direction character is looking"""
        # open inventory
        character.foreign_inventory = self["inventory"]
        character["open_inventory"] = True

@register_item("CHEST")
class ChestItem(Item):
    def use_on_block(self,character,blockpos,face):
        new_pos = blockpos + face
        block_id = self.item["id"]
        r = int((character["rotation"][0] + 45) // 90) % 4
        inventory = ObservableDict()
        for i in range(28):
            inventory[i] = {"id":"AIR"}
        character.world[new_pos] = {"id":block_id,"rotation":r,"inventory":inventory}
