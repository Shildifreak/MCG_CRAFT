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
            block = self.world.blocks[dpos+self.position]
            if block["p_ambient"] or -dpos in block["p_directions"]:
                level = block["p_stronglevel"]
                if level == None:
                    level = block["p_level"]
                maxpower = max(maxpower, level)
        p_level = maxpower - 1
        if self["p_level"] != p_level:
            self["p_level"] = p_level
            self["state"] = str(p_level)
            return True
        return False

    def collides_with(self,area):
        return False

    def get_tags(self):
        return (super().get_tags() - {"solid"}) | {"block_update"}

#        Block.block_update(self,faces)

@register_item("Redstone")
class Redstone_Item(Item):
    def block_version(self):
        return {"id":self.item["id"],"state":"0"}

@register_block("Repeater")
class Repeater(Block):
    def handle_event_block_update(self,event):
        d = self.get_front_facing_vector()
        self["p_directions"] = (d,)
        
        source = self.world.blocks[self.position - d]
        if source["p_level"] and (source["p_ambient"] or (d in source["p_directions"])):
            self["state"] = ""
            self["p_level"] = 15
        else:
            self["state"] = ""
            self["p_level"] = 0
        return True

    #def activated(self,character,face):
    #    d = self.get_front_facing_vector()
    #    self.world[self.position+d] = {
    #        "id":"Repeater",
    #        "rotation":self["rotation"]}

    def get_tags(self):
        return super().get_tags() | {"block_update"}





        
