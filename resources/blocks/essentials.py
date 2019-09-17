from resources import *


@register_block("AIR")
class AirBlock(Block):
    def get_tags(self):
        return set() # no solid tag, no explosion tag
    def collides_with(self,area):
        return False



@register_block("BEDROCK")
@register_block("mcgcraft:bedrock")
class StoneBlock(Block):
    blast_resistance = 1
    def activated(self,character,face):
        """something like placing block depending on direction character is looking"""
        # what should happen if you rightclick bedrock?

    def mined(self,character,face):
        """can't mine bedrock, so this function does nothing instead of default something"""
        print("hey, you can't mine bedrock")

    def get_tags(self):
        return super(StoneBlock,self).get_tags() - {"explosion"} # can't explode
