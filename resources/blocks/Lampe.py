from resources import *

@register_block("LAMP")
class lampean(SolidBlock):
    def block_update(self,faces):
        print "got blockupdated"
        SolidBlock.block_update(self,faces)
        for face in FACES:
            nachbarblockposition = self.position + face
            nachbarblock = self.world[nachbarblockposition]
            if nachbarblock["p_level"] and nachbarblock["p_ambient"]:
                self["state"] = "ON"
                return
        self["state"] = "OFF"
