from resources import *


@register_block("SAND")
class FallingBlock(Block):
    def get_tags(self):
        return set.union(Block.get_tags(self),{"block_update"})
    def handle_event_block_update(self,event):
        print("sand got block updated")
        if self.relative[(0,-1,0)] == "AIR":
            #M# change to move request
            self.relative[(0,-1,0)] = {"id":self["id"]}
            self.relative[(0,0,0)] = "AIR"
