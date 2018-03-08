from base import *


@register_block("CHEST")
class ChestBlock(Block):
    def activated(self,character,face):
        """something like placing block depending on direction character is looking"""
        # open inventory
        character.foreign_inventory = character["inventory"]
        character["open_inventory"] = True

@register_item("CHEST")
class ChestItem(Item):
    def use_on_block(self,character,blockpos,face):
        new_pos = blockpos + face
        block_id = self.item["id"]
        r = int((character["rotation"][0] + 45) // 90) % 4
        character.world[new_pos] = block_id + ":%i" % r
        
