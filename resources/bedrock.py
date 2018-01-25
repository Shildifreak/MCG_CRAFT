from base import *


@register_block("STONE")
@register_block("mcgcraft:bedrock")
class StoneBlock(Block):
    def activated(self,character,face):
        """something like placing block depending on direction character is looking"""
        # what should happen if you rightclick bedrock?

    def mined(self,character,face):
        """can't mine bedrock, so this function does nothing instead of default something"""
        print("hey, you can't mine bedrock")
