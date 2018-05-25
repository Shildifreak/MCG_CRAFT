# -*- coding: utf-8 -*-
from resources import *

@register_block("Redstone")
class Redstone(Block):
    defaults = Block.defaults.copy()
    defaults["p_directions"] = (Vector((1,0,0)),Vector((-1,0,0)),Vector((0,0,1)),Vector((0,0,-1)),Vector((0,-1,0)))
    def block_update(self,faces):
        connections = FACES[:]
        # hier weitere verbindungen einfügen (für diagonalen)
        maxpower = 1
        for dpos in connections:
            block = self.world[dpos+self.position]
            if block["p_ambient"] or -dpos in block["p_directions"]:
                level = block["p_stronglevel"]
                if level == None:
                    level = block["p_level"]
                maxpower = max(maxpower, level)
        self["p_level"] = maxpower - 1
        self["state"] = str(self["p_level"])
    def collides_with(self,hitbox,position):
        return False

#        Block.block_update(self,faces)

@register_item("Redstone")
class Redstone_Item(Item):
    def use_on_block(self,character,blockpos,face):
        new_pos = blockpos + face
        block_id = self.item["id"]
        character.world[new_pos] = {"id":block_id,"state":"0"}
        #M# remove block again if it collides with placer (check for all entities here later)
        if new_pos in character.collide(character["position"]):
            character.world[new_pos] = "AIR"
