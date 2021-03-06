from resources import *
import falling

@register_block("FAN")

class fanblock(falling.FallingBlock):

    def get_tags(self):
        return super().get_tags() | {"block_update"}

    def handle_event_block_update(self,event):
        if self.redstone_activated() and self.get("last_push",0) < self.world.clock.current_gametick:
            direction = -self.get_base_vector()
            p1 = self.position + direction
            p2 = p1 + direction
            if self.world.blocks[p1] != "AIR" and self.world.blocks[p2] == "AIR":
                self.world.request_move_block(p1,p2)
                self["last_push"]=self.world.clock.current_gametick
        super().handle_event_block_update(event)
        return True
