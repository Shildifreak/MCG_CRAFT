spawnpoint = (0,10,-3)
terrain_generator = []
def init(welt):


    for x in range(-21,22):
        for z in range(-5,30):
            welt[(x,-2,z)] = "BEDROCK"
            if z > 5:
                welt[(x,-1,z)] = "AIM"
            if z == -1:
                welt[(x,0,z)] = "BEDROCK"
                welt[(x,2,z)] = "BEDROCK"
            if z == 29 or z == -5 or x == -21 or x == 21:
                welt[(x,-1,z)] = "BEDROCK"
                welt[(x,0,z)] = "BEDROCK"
                welt[(x,1,z)] = "BEDROCK"
            if z < 6:
                welt[(x,-1,z)] = "BEDROCK"

    welt[(0,0,-1)] = "DOORBOTTOM"
    welt[(0,1,-1)] = "DOORTOP"
