from base import *

@register_item("mcgcraft:grass")
class GrassItem(Item):
    def use_on_block(self,character,blockpos,face):
        """place some grass"""



@register_block("STONE")
@register_block("mcgcraft:bedrock")
class StoneBlock(Block):
    def activated(self,character):
        """something like placing block depending on direction character is looking"""

    def mined(self,character):
        """can't mine bedrock, so this function does nothing instead of default something"""
        print("hey, you can't mine bedrock")
