from resources import *

@register_block("TORCH")
class Torch(Block):
    def block_update(self,directions):
        a = 0
        for direction in directions:
            block = self.world[self.position+direction]
            if block["p_level"]:
                self["p_level"] = 0
                self["p_stronglevel"] = 0
                self["p_directions"] = ()
                a += 1
        if a == 0:
            self["p_level"] = 15
            self["p_stronglevel"] = 15
            self["p_directions"] = ((0,1,0),)
    def collides_with(self,hitbox,position):
        return False
    
