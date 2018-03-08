from base import *

@register_block("DOORTOP")

class DoorTop(Block):
    blast_resistance = 0
    def activated(self,character,face):
        pos = self.position
        self.world[pos] = "AIR"
        self.world[pos-(0,1,0)] = "AIR"
    def mined(self,character,face):
        pass

@register_block("DOORBOTTOM")

class DoorBottom(Block):
    blast_resistance = 0
    def activated(self,character,face):
        pos = self.position
        self.world[pos] = "AIR"
        self.world[pos+(0,1,0)] = "AIR"
    def mined(self,character,face):
        pass

@register_block("DOORSTEP")

class DoorStep(Block):
    blast_resistance = 0
    def activated(self,character,face):
        pos = self.position
        self.world[pos+(0,1,0)] = "DOORBOTTOM"
        self.world[pos+(0,2,0)] = "DOORTOP"
