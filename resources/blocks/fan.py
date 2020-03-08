from resources import *

@register_block("FAN")

class fanblock(Block):

    def get_tags(self):
        return super().get_tags() + {"block_update"}

    def handle_event_block_update(self,event):
        if self.redstone_activated():
            direction = -self.get_base_vector()
            p1 = self.position + direction
            p2 = p1 + direction
            if self.world.blocks[p1] != "AIR" and self.world.blocks[p2] == "AIR":
                self.world.request_move_block(p1,p2)
