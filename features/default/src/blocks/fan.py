from resources import *
import falling


class FAN(falling._FallingBlock):

    def get_tags(self):
        return super().get_tags() | {"block_update"}

    def handle_event_block_update(self,event):
        level = self.ambient_power_level()
        if level > 0 and self.get("last_push",0) < self.world.clock.current_gametick:
            direction = -self.get_base_vector()
            for offset in range(1, level+1):
                p1 = self.position + direction*offset
                if self.world.blocks[p1] != "AIR":
                    break
            p2 = p1 + direction
            if self.world.blocks[p2] == "AIR":
                self.world.request_move_block(p1,p2)
                self["last_push"]=self.world.clock.current_gametick
                return True
        return super().handle_event_block_update(event)
