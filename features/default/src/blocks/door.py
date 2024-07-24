from resources import *

class _Door(Block):
    defaults = Block.defaults.copy()
    defaults["state"] = ""
    blast_resistance = 0
    #offset = -1 / 1      # y offset to get to other half of door
    
    def clicked(self,character,face,item):
        if self.ambient_power_level() != 0:
            return
        new_state = "" if self["state"] else "OPEN"
        self.relative[(0,self.offset_top   ,0)] = {"id":"DOORTOP"   , "state":new_state}
        self.relative[(0,self.offset_bottom,0)] = {"id":"DOORBOTTOM", "state":new_state}

    def mined(self,character,face):
        self.relative[(0,self.offset_top   ,0)] = "AIR"
        self.relative[(0,self.offset_bottom,0)] = "AIR"
        super().mined(character, face)

    def ambient_power_level(self):
        ambient_power = PowerLevelAccumulator()
        for face in FACES:
            for offset in [self.offset_top, self.offset_bottom]:
                neighbour = self.relative[-face+(0,offset,0)]
                if neighbour["p_ambient"] or (face in neighbour["p_directions"]):
                    ambient_power.add(neighbour["p_level"])
        return ambient_power.level

    def handle_event_block_update(self,event):
        power = self.ambient_power_level()
        if power != 0:
            new_state = "OPEN" if power > 0 else ""
            if new_state != self["state"]:
                self["state"] = new_state
                return True
        return False

    def item_version(self):
        """use the output of this function when turning the block into an item"""
        return {"id":"DOOR","count":1}

    def get_tags(self):
        tags = super().get_tags() | {"block_update"}
        if self["state"] == "OPEN":
            tags.discard("solid")
        return tags

#    def collides_with(self,area):
#        return self["state"] != "OPEN"

class DOORTOP(_Door):
    offset_top    =  0
    offset_bottom = -1

class DOORBOTTOM(_Door):
    offset_top    =  1
    offset_bottom =  0


@alias("DOORTOP")
@alias("DOORBOTTOM")
class DOOR(Item):
    def block_version(self):
        # always place as DOORBOTTOM
        return "DOORBOTTOM"
    def use_on_block(self,character,block,face):
        super().use_on_block(character,block,face)
        # after placing of DOORBOTTOM add DOORTOP
        world = character.world
        upper_half_pos = block.position + face + (0,1,0)
        if world.blocks[upper_half_pos] == "AIR":
            world.blocks[upper_half_pos] = "DOORTOP"
