from base import *


@register_block("CHEST")
class StoneBlock(Block):
    def activated(self,character,face):
        """something like placing block depending on direction character is looking"""
        # open inventory
        character.foreign_inventory = character["inventory"]
        character["open_inventory"] = True
