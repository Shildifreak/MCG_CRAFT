from resources import *

class SnailSoul(EntitySoul):
    def __init__(self, entity):
        self.entity = entity
        self.state = {
            "forward" : False,
            "turn" : 0,
        }
    
    def update(self):
        r = random.randint(0,2000)
        if r < 1:
            self.state["turn"] = -0.02
            self.state["forward"] = True
        elif r < 2:
            self.state["turn"] = 0.02
            self.state["forward"] = True
        elif r < 6:
            self.state["turn"] = 0
            self.state["forward"] = True
        elif r < 10:
            self.state["turn"] = 0
            self.state["forward"] = False
        
        sx, _, sz = self.entity.get_sight_vector()
        if self.state["forward"]:
            self.entity.ai_commands["x"].append(sx)
            self.entity.ai_commands["z"].append(sz)

        jump = (self.state["forward"] and 
            (self.entity.world.blocks[(self.entity["position"] + Vector(sx,-0.5,sz)).round()] != "AIR"))
        self.entity.ai_commands["jump"].append(jump)
        
        y, p = self.entity["rotation"]
        y += self.state["turn"]
        self.entity.ai_commands["yaw"].append(y)
        self.entity.ai_commands["pitch"].append(p)

class Snail(Entity):
    HITBOX = Hitbox(14/16/2,10/16,8/16)
    LIMIT = 5
    instances = []
    
    def __init__(self, data = None):
        data_defaults = {
            "texture" : "SNAIL",
            "SPEED" : 0.1,
            "JUMPSPEED" : 8,
            "tags" : {"update"},
        }
        if data != None:
            data_defaults.update(data)
        super().__init__(data_defaults)
        self.ai = SnailSoul(self)

    def clicked(self, character, item):
        character.pickup_item({"id":"Glue"})
        self.kill()

    def update(self):
        self.ai.update()
        self.execute_ai_commands()
