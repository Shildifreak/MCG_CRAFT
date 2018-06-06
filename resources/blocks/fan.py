from resources import *

@register_block("FAN")

class fanblock(Block):

    def block_update(self,faces):
        if self.redstone_activated():
            direction = -self.get_base_vector()
            p1 = self.position + direction
            p2 = p1 + direction
            if self.world[p1] != "AIR" and self.world[p2] == "AIR":
                self.world.request_move_block(p1,p2)
