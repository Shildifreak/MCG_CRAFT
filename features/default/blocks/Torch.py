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
        return False
    
    def handle_event_redstone_update(self, event):
        # check block torch is attached to for redstone signal
        basevector = self.get_base_vector()
        source = self.world.blocks.get(self.position + basevector, t=-1)
        source_level = source["p_level"] if (source["p_ambient"] or (-basevector in source["p_directions"])) else 0
        new_state_and_p_level = [
            ("RED",   15),
            ("OFF" ,   0),
            ("BLUE", -15)
            ][1 + (source_level > 0) - (source_level < 0)]
        if new_state_and_p_level != (self["state"], self["p_level"]):
            self["state"], self["p_level"] = new_state_and_p_level
            return True
        return False


    #def collides_with(self,area):
    #    return False

    def get_tags(self):
        return (super().get_tags() - {"solid"}) | {"block_update", "redstone_update"}
