from resources import *

class Door(Block):
    defaults = Block.defaults.copy()
    defaults["state"] = ""
    blast_resistance = 0
    #offset = -1 / 1      # y offset to get to other half of door
    
    def activated(self,character,face):
        new_state = "" if self["state"] else "OPEN"
        self.relative[(0,self.offset_top   ,0)] = {"id":"DOORTOP"   , "state":new_state}
        self.relative[(0,self.offset_bottom,0)] = {"id":"DOORBOTTOM", "state":new_state}

    def mined(self,character,face):
        self.relative[(0,self.offset_top   ,0)] = "AIR"
        self.relative[(0,self.offset_bottom,0)] = "AIR"
        super().mined(character, face)

    def item_version(self):
        """use the output of this function when turning the block into an item"""
        return {"id":"DOOR","count":1}

    def collides_with(self,area):
        return self["state"] != "OPEN"

@register_block("DOORTOP")

class DoorTop(Door):
    offset_top    =  0
    offset_bottom = -1

@register_block("DOORBOTTOM")

class DoorBottom(Door):
    offset_top    =  1
    offset_bottom =  0


@register_item("DOOR")
@register_item("DOORTOP")
@register_item("DOORBOTTOM")
class DoorItem(Item):
    def block_version(self):
        # always place as DOORBOTTOM
        return "DOORBOTTOM"
    def use_on_block(self,character,blockpos,face):
        super().use_on_block(character,blockpos,face)
        # after placing of DOORBOTTOM add DOORTOP
        world = character.world
        upper_half_pos = blockpos + face + (0,1,0)
        if world.blocks[upper_half_pos] == "AIR":
            world.blocks[upper_half_pos] = "DOORTOP"
