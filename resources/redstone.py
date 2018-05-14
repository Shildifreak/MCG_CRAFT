from base import *

@register_block("Redstone")
class Redstone(Block):
    def block_update(self,faces):
        Block.block_update(self,faces)

@register_item("Redstone")
class Redstone_Item(Item):
    def use_on_block(self,character,blockpos,face):
        new_pos = blockpos + face
        block_id = self.item["id"]
        character.world[new_pos] = {"id":block_id,"state":0}
        #M# remove block again if it collides with placer (check for all entities here later)
        if new_pos in character.collide(character["position"]):
            character.world[new_pos] = "AIR"
