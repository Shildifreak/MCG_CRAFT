from resources import *


@register_block("SAND")
class FallingBlock(Block):
    def block_update(self,directions):
        if self.relative[(0,-1,0)] == "AIR":
            #M# change to move request
            self.relative[(0,-1,0)] = {"id":self["id"]}
            self.relative[(0,0,0)] = "AIR"
