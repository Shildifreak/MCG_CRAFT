from base import *

@register_block("LAMPON")
class lampean(Block):
    def block_update(self,faces):
        for face in faces:
            nachbarblockposition = self.position + face
            nachbarblock = self.world[nachbarblockposition]
            if nachbarblock["powered"]:
                return
        return "LAMPOFF"
@register_block("LAMPOFF")
class lampeaus(Block):
    def block_update(self,faces):
        for face in faces:
            nachbarblockposition = self.position + face
            nachbarblock = self.world[nachbarblockposition]
            if nachbarblock["powered"]:
                return("LAMPON")
