from resources import *


@register_block("SAND")
class FallingBlock(Block):
    def block_update(self,directions):
        if self.world[self.position+(0,-1,0)] == "AIR":
            self.world[self.position+(0,-1,0)] = {"id":self["id"]}
            self.world[self.position] = "AIR"
