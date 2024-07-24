# -*- coding: utf-8 -*-
from resources import *

class Redstone(Block):
    defaults = Block.defaults.copy()
    defaults["p_directions"] = (Vector((1,0,0)),Vector((-1,0,0)),Vector((0,0,1)),Vector((0,0,-1)),Vector((0,-1,0)))
    
    def handle_event_block_update(self,event):
        connections = FACES[:]
        # hier weitere verbindungen einfügen (für diagonalen)
        pla = PowerLevelAccumulator()
        for dpos in connections:
            block = self.relative[dpos]
            if block["p_ambient"] or -dpos in block["p_directions"]:
                level = block["p_stronglevel"]
                if level == None:
                    level = block["p_level"]
                pla.add(level)
        maxpower = pla.level
        p_level = maxpower - (maxpower > 0) + (maxpower < 0)
        if self["p_level"] != p_level:
            self["p_level"] = p_level
            self["state"] = str(p_level)
            return True
        return False

#    def collides_with(self,area):
#        return False

    def get_tags(self):
        return (super().get_tags() - {"solid"}) | {"block_update"}

#        Block.block_update(self,faces)

class Redstone(Item):
    def block_version(self):
        return {"id":self.item["id"],"state":"0"}

class Repeater(Block):
    def handle_event_block_update(self,event):
        d = self.get_front_facing_vector()
        self["p_directions"] = (d,)
        
        source = self.world.blocks.get(self.position - d, t=-1)
        source_level = source["p_level"] if (source["p_ambient"] or (d in source["p_directions"])) else 0
        new_p_level = 15 * ((source_level > 0) - (source_level < 0))
        if new_p_level != self["p_level"]:
            self["p_level"] = new_p_level
            self["state"] = ""
            return True
        return False

    #def activated(self,character,face):
    #    d = self.get_front_facing_vector()
    #    self.world[self.position+d] = {
    #        "id":"Repeater",
    #        "rotation":self["rotation"]}

    def get_tags(self):
        return super().get_tags() | {"block_update"}





        
