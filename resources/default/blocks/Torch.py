from resources import *
from voxelengine.modules.geometry import Point
from voxelengine.server.event_system import Event

@register_block("TORCH")
class Torch(Block):
    defaults = Block.defaults.copy()
    defaults["p_directions"] = (Vector((0,1,0)),)
    defaults["p_ambient"] = True
    def handle_event_block_update(self,event):
        redstone_update = Event("redstone_update",Point(self.position))
        self.world.event_system.add_event(redstone_update, 1)

    
    def handle_event_redstone_update(self, event):
        # check block torch is attached to for redstone signal
        basevector = self.get_base_vector()
        block = self.world.blocks.get(self.position + basevector, t=-1)
        if block["p_level"]:
            self["state"] = "OFF"
            self["p_level"] = 0
        else:
            self["state"] = "ON"
            self["p_level"] = 15
        self.save()

    def collides_with(self,hitbox,position):
        return False

    def get_tags(self):
        return (super().get_tags() - {"solid"}) | {"block_update", "redstone_update"}
