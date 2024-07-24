from resources import *
import random

class SchafSoul(EntitySoul):
    def __init__(self, entity):
        self.entity = entity
        self.state = {
            "forward" : False,
            "turn" : 0,
            "nod" : False,
        }
    
    def update(self):
        r = random.randint(0,200)
        if r < 1:
            self.state["turn"] = -5
            self.state["nod"] = False
        elif r < 2:
            self.state["turn"] = 5
            self.state["nod"] = False
        elif r < 3:
            self.state["forward"] = True
            self.state["turn"] = 0
            self.state["nod"] = False
        elif r < 5:
            self.state["forward"] = False
            self.state["nod"] = False
        elif r < 7:
            self.state["forward"] = False
            self.state["turn"] = 0
            self.state["nod"] = True
        
        sx, _, sz = self.entity.get_sight_vector()
        if self.state["forward"]:
            self.entity.ai_commands["x"].append(sx)
            self.entity.ai_commands["z"].append(sz)

        if self.state["forward"]:
            jump = self.entity.world.blocks[(self.entity["position"] + Vector(sx,-0.5,sz)).round()] != "AIR"
        else:
            jump = not random.randint(0,2000)
        if jump:
            self.entity.ai_commands["jump"].append(jump)
        
        y, p = self.entity["rotation"]
        y += self.state["turn"]
        p = -self.state["nod"]*50
        self.entity.ai_commands["yaw"].append(y)
        self.entity.ai_commands["pitch"].append(p)        


class Schaf(Entity):
    HITBOX = Hitbox(0.6,1.5,1)
    LIMIT = 5
    instances = []
    
    def __init__(self, data = None):
        data_defaults = {
            "texture" : "SCHAF",
            "SPEED" : 10,
            "JUMPSPEED" : 10,
            "tags" : {"update"},
        }
        if data != None:
            data_defaults.update(data)
        super().__init__(data_defaults)
        self.ai = SchafSoul(self)

    def clicked(self, character, item):
        self["texture"] = "SCHAF,GESCHOREN"
        character.pickup_item({"id":"WEISS"})

    def update(self):

        if self["position"][1] < -100:
            self.kill()
            return

        self.ai.update()
        self.execute_ai_commands()

        y, p = self["rotation"]
        if p <= -50:
            pos = (self["position"]+Vector(0,-2,0)).round()
            if self.world.blocks[pos] == "GRASS":
                self.world.blocks[pos] = "DIRT"
                self["texture"] = "SCHAF"
