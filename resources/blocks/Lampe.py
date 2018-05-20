from resources import *

@register_block("LAMPON")
class lampean(SolidBlock):
    def block_update(self,faces):
        print "got blockupdated"
        SolidBlock.block_update(self,faces)
        for face in FACES:
            nachbarblockposition = self.position + face
            nachbarblock = self.world[nachbarblockposition]
            if nachbarblock["p_level"] and nachbarblock["p_ambient"]:
                return
        self["id"] = "LAMPOFF"
@register_block("LAMPOFF")
class lampeaus(SolidBlock):
    def block_update(self,faces):
        print "got blockupdated"
        SolidBlock.block_update(self,faces)
        for face in FACES:
            nachbarblockposition = self.position + face
            nachbarblock = self.world[nachbarblockposition]
            if nachbarblock["p_level"] and nachbarblock["p_ambient"]:
                self["id"] = "LAMPON"
