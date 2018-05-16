from mcgcraft import Block, register_block

@register_block("DOORTOP")

class DoorTop(Block):
    blast_resistance = 0
    def activated(self,character,face):
        pos = self.position
        self.world[pos] = "DOORTOPOPEN"
        self.world[pos-(0,1,0)] = "DOORBOTTOMOPEN"
    def mined(self,character,face):
        pass

@register_block("DOORBOTTOM")

class DoorBottom(Block):
    blast_resistance = 0
    def activated(self,character,face):
        pos = self.position
        self.world[pos] = "DOORBOTTOMOPEN"
        self.world[pos+(0,1,0)] = "DOORTOPOPEN"
    def mined(self,character,face):
        pass

@register_block("DOORSTEP")

class DoorStep(Block):
    blast_resistance = 0
    def activated(self,character,face):
        pos = self.position
        self.world[pos+(0,1,0)] = "DOORBOTTOM"
        self.world[pos+(0,2,0)] = "DOORTOP"

@register_block("DOORTOPOPEN")

class DoorTopOpen(Block):
    blast_resistance = 0
    def activated(self,character,face):
        pos = self.position
        self.world[pos] = "DOORTOP"
        self.world[pos-(0,1,0)] = "DOORBOTTOM"
    def mined(self,character,face):
        pass
    def collides_with(self,entity):
        return False

@register_block("DOORBOTTOMOPEN")

class DoorBottomOpen(Block):
    blast_resistance = 0
    def activated(self,character,face):
        pos = self.position
        self.world[pos] = "DOORBOTTOM"
        self.world[pos+(0,1,0)] = "DOORTOP"
    def mined(self,character,face):
        pass
    def collides_with(self,entity):
        return False
