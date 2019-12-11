from resources import *


@register_block("SAND")
class FallingBlock(Block):
    def get_tags(self):
        return set.union(Block.get_tags(self),{"block_update"})
    def handle_event_block_update(self,events):
        print("sand %s got block updated" %str(self.position))
        if self.relative[(0,-1,0)] == "AIR":
            #self.relative[(0,-1,0)] = {"id":self["id"]}
            #self.relative[(0,0,0)] = "AIR"
            self.world.request_move_block(self.position, self.position + (0,-1,0))
