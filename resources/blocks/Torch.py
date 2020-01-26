from resources import *
from voxelengine.modules.geometry import Point
from voxelengine.server.event_system import Event

@register_block("TORCH")
class Torch(Block):
    defaults = Block.defaults.copy()
    defaults["p_directions"] = (Vector((0,1,0)),)
    def handle_event_block_update(self,event):
        print("redstone torch got block updated")
        self.world.event_system.add_event(1,Event("redstone_update",Point(self.position)))

    
    def handle_event_redstone_update(self, event):
        # check block torch is attached to for redstone signal
        print("redstone torch got redstone updated")
        basevector = self.get_base_vector()
        block = self.world.blocks.get(self.position + basevector, t=-1)
        if block["p_level"]:
            self["state"] = "OFF"
            self["p_level"] = 0
            self["p_stronglevel"] = 0
        else:
            self["state"] = "ON"
            self["p_level"] = 15
            self["p_stronglevel"] = 15
        self.save()

    def collides_with(self,hitbox,position):
        return False

    def get_tags(self):
        return super(Torch,self).get_tags().union({"block_update", "redstone_update"}) - {"solid"}
