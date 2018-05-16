import mcgcraft

class Einhorn(mcgcraft.Entity):
    LIMIT = 5
    
    def __init__(self,world):
        super(Einhorn,self).__init__()
        
        self["texture"] = "EINHORN"
        self["SPEED"] = 5
        self["JUMPSPEED"] = 10
        self["hitbox"] = get_hitbox(0,0,0)
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
        einhoerner.append(self)
    def update(self):
        pass
