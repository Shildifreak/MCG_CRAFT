from resources import *

@register_block("TORCH")
class Torch(Block):
    defaults = Block.defaults.copy()
    defaults["p_directions"] = (Vector((0,1,0)),)
    def handle_event_block_update(self,event):
        # check block torch is attached to for redstone signal
        print("redstone torch got block updated")
        basevector = self.get_base_vector()
        block = self.world[self.position + basevector]
        changed = False
        if block["p_level"]:
            if self["state"] != "OFF":
                self["state"] = "OFF"
                self["p_level"] = 0
                self["p_stronglevel"] = 0
                self.save()
        else:
            if self["state"] != "ON":
                self["state"] = "ON"
                self["p_level"] = 15
                self["p_stronglevel"] = 15
                self.save()

    def collides_with(self,hitbox,position):
        return False

    def get_tags(self):
        return super(Torch,self).get_tags().union({"block_update"}) - {"solid"}
