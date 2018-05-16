from mcgcraft import Block, register_block, FACES

@register_block("LAMPON")
class lampean(Block):
    def block_update(self,faces):
        for face in FACES:
            nachbarblockposition = self.position + face
            nachbarblock = self.world[nachbarblockposition]
            if nachbarblock["p_level"] and nachbarblock["p_ambient"]:
                return Block.block_update(self,faces)
        return "LAMPOFF"
@register_block("LAMPOFF")
class lampeaus(Block):
    def block_update(self,faces):
        for face in faces:
            nachbarblockposition = self.position + face
            nachbarblock = self.world[nachbarblockposition]
            if nachbarblock["p_level"] and nachbarblock["p_ambient"]:
                return("LAMPON")
        return Block.block_update(self,faces)
