from resources import *
import random

@register_entity("Schaf")

class Schaf(Entity):
    HITBOX = Hitbox(0.6,1.5,1)
    LIMIT = 5
    instances = []
    
    def __init__(self):
        super().__init__()

        self["texture"] = "SCHAF"
        self["SPEED"] = 10
        self["JUMPSPEED"] = 10
        self["forward"] = False
        self["turn"] = 0
        self["nod"] = False
        self["tags"] = {"update"}

    def right_clicked(self, character):
        self["texture"] = "SCHAF,GESCHOREN"
        
    def left_clicked(self, character):
        print("Maehhh")

    def update_ai(self):
        r = random.randint(0,200)
        if r < 1:
            self["turn"] = -5
            self["nod"] = False
        elif r < 2:
            self["turn"] = 5
            self["nod"] = False
        elif r < 3:
            self["forward"] = True
            self["turn"] = 0
            self["nod"] = False
        elif r < 5:
            self["forward"] = False
            self["nod"] = False
        elif r < 7:
            self["forward"] = False
            self["turn"] = 0
            self["nod"] = True
        
        sx, _, sz = self.get_sight_vector()
        self.ai_commands["x"].append(sx * self["forward"])
        self.ai_commands["z"].append(sz * self["forward"])

        if self["forward"]:
            jump = self.world.blocks[(self["position"] + Vector(sx,-0.5,sz)).round()] != "AIR"
        else:
            jump = not random.randint(0,2000)
        if jump:
            self.ai_commands["jump"].append(jump)

    def update(self):
        self.update_dt()

        if self["position"][1] < -100:
            self.kill()
            return

        self.update_ai()

        self.execute_ai_commands()

        y, p = self["rotation"]
        dy = self["turn"]
        dp = -self["nod"]*50 - p
        if dy or dp:
            self["rotation"] = y+dy, p+dp

        if p <= -50:
            pos = (self["position"]+Vector(0,-2,0)).round()
            if self.world.blocks[pos] == "GRASS":
                self.world.blocks[pos] = "DIRT"
