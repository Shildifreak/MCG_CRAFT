from resources import *

@register_block("LAMP")
class lampean(SolidBlock):
    def block_update(self,faces):
        SolidBlock.block_update(self,faces)
        if self.redstone_activated():
            self["state"] = "ON"
        else:
            self["state"] = "OFF"
