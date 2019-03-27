from resources import *
import time, random

@register_entity("DAME")

class Dame(Entity):
    HITBOX = Hitbox(0.6,3,1.5)
    LIMIT = 1
    instances = []
    
    def __init__(self, world):
        super(Dame,self).__init__()

        self["texture"] = "DAME"
        self["SPEED"] = 5
        self["JUMPSPEED"] = 10
        self["sprint"] = 20
        self["velocity"] = Vector([0,0,0])
        self["last_update"] = time.time()
        self["forward"] = False
        self["turn"] = 0

    #def right_clicked(self, character):
    #    print "Muuhhh"
        
    #def left_clicked(self, character):
    #    print "Maehhh"

    def update(self):
        self.update_dt()

        if self.world.players:
            player = random.choice(tuple(self.world.players))
            richtung = player.entity["position"] - self["position"]
            self["velocity"] = richtung.normalize()*1.3
        else:
            self["velocity"] = Vector((0,0,0))
        self.update_position()

##        r = random.randint(0,200)
##        if r < 1:
##            self["turn"] = -5
##        elif r < 2:
##            self["turn"] = 5
##        elif r < 3:
##            self["forward"] = True
##            self["turn"] = 0
##        elif r < 5:
##            self["forward"] = False
##        
##        self.update_dt()
##        nv = Vector([0,0,0])
##        sx,sy,sz = self.get_sight_vector()
##        if self["forward"]:
##            nv += Vector((sx,0,sz))*self["SPEED"]
##            jump = self.world.get_block((self["position"]+Vector((sx,-0.5,sz))).normalize()) != "AIR"
##        else:
##            jump = not random.randint(0,2000)
##        sv = self.horizontal_move(jump)
##        self["velocity"] += ((1,1,1)-sv)*nv
##        self.update_position()
##        y, p = self["rotation"]
##        dy = self["turn"]
##        dp =  - p
##        if dy or dp:
##            self["rotation"] = y+dy, p+dp
