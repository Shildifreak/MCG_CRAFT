from resources import *


@register_block("SAND")
class FallingBlock(Block):
    def get_tags(self):
        return super().get_tags() | {"block_update","fall"} 
    def handle_event_block_update(self,events):
        if self.relative[(0,-1,0)] == "AIR":
            self.world.event_system.add_event(2,Event("fall",Point(self.position)))
    def handle_event_fall(self,event):
        if self.relative[(0,-1,0)] == "AIR":
            self.world.request_move_block(self.position, self.position + (0,-1,0))
