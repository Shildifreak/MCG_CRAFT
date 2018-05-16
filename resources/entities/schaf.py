import mcgcraft

class Schaf(mcgcraft.Entity):
    LIMIT = 2
    
    def __init__(self, world):
        super(Schaf,self).__init__()

        self["texture"] = "SCHAF"
        self["SPEED"] = 5
        self["JUMPSPEED"] = 10
        self["hitbox"] = get_hitbox(0.6,1.5,1)
        self["sprint"] = 20
        self.set_world(world,(0,0,0))
        while True:
            x = random.randint(-40,40)
            z = random.randint(-10,10)
            y = random.randint(-40,40)
            block = world.get_block((x,y-2,z),load_on_miss = False)
            if block and block != "AIR" and len(self.collide(Vector((x,y,z)))) == 0:
                break
        self["position"] = (x,y,z)
        self["velocity"] = Vector([0,0,0])
        self["last_update"] = time.time()
        self["forward"] = False
        self["turn"] = 0
        self["nod"] = False
        schafe.append(self)

    def update(schaf):
        r = random.randint(0,200)
        if r < 1:
            schaf["turn"] = -5
            schaf["nod"] = False
        elif r < 2:
            schaf["turn"] = 5
            schaf["nod"] = False
        elif r < 3:
            schaf["forward"] = True
            schaf["turn"] = 0
            schaf["nod"] = False
        elif r < 5:
            schaf["forward"] = False
            schaf["nod"] = False
        elif r < 7:
            schaf["forward"] = False
            schaf["turn"] = 0
            schaf["nod"] = True
        
        schaf.update_dt()
        nv = Vector([0,0,0])
        sx,sy,sz = schaf.get_sight_vector()
        if schaf["forward"]:
            nv += Vector((sx,0,sz))*schaf["SPEED"]
            jump = schaf.world.get_block((schaf["position"]+Vector((sx,-0.5,sz))).normalize()) != "AIR"
        else:
            jump = not random.randint(0,2000)
        sv = schaf.horizontal_move(jump)
        schaf["velocity"] += ((1,1,1)-sv)*nv
        schaf.update_position()
        y, p = schaf["rotation"]
        dy = schaf["turn"]
        dp = -schaf["nod"]*50 - p
        if dy or dp:
            schaf["rotation"] = y+dy, p+dp
