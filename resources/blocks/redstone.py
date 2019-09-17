# -*- coding: utf-8 -*-
from resources import *

@register_block("Redstone")
class Redstone(Block):
    defaults = Block.defaults.copy()
    defaults["p_directions"] = (Vector((1,0,0)),Vector((-1,0,0)),Vector((0,0,1)),Vector((0,0,-1)),Vector((0,-1,0)))
    
    def handle_event_block_update(self,event):
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

    def collides_with(self,area):
        return False

    def get_tags(self):
        return super(Redstone,self).get_tags().union({"block_update"}) - {"solid"}

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
        else:
            self.item["count"] -= 1
        if self.item["count"] <= 0:
            self.item.parent[self.item.parent_key] = {"id": "AIR"}


@register_block("Repeater")
class Repeater(Block):
    def handle_event_block_update(self,event):
        d = self.get_front_facing_vector()
        self["p_directions"] = (d,)
        
        source = self.world[self.position - d]
        if "strong powered" or ("weak powered" and "correct direction"):
            "do stuff"
        # tbc.

    def activated(self,character,face):
        d = self.get_front_facing_vector()
        self.world[self.position+d] = {
            "id":"Repeater",
            "rotation":self["rotation"]}

    def get_tags(self):
        return super(Repeater,self).get_tags().union({"block_update"})





        
