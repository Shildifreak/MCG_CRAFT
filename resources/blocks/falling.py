from resources import *


@register_block("SAND")
class FallingBlock(Block):
    def get_tags(self):
        return super().get_tags() + {"block_update"}
    def handle_event_block_update(self,events):
        if self.relative[(0,-1,0)] == "AIR":
            self.world.request_move_block(self.position, self.position + (0,-1,0))
