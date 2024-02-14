from resources import *

@register_block("Fence")
class FenceBlock(Block):

    def handle_event_block_update(self,event):
        state = 0
        for i, offset in enumerate(((0,0,-1),(1,0,0),(0,0,1),(-1,0,0))):
            if self.relative[offset] != "AIR":
                state |= 1 << i
        state = str(state)
        
        if state != self["state"]:
            self["state"] = state
            return True
        return False

    def get_tags(self):
        return super().get_tags() | {"block_update"}


@register_item("Fence")
class FenceItem(Item):
    def block_version(self):
        return {"id":self.item["id"],"state":"0"}
