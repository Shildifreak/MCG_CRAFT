spawnpoint = (0,10,-3)

def init(welt):


    for x in range(-21,22):
        for z in range(-5,30):
            welt.blocks[(x,-2,z)] = "BEDROCK"
            if z > 5:
                welt.blocks[(x,-1,z)] = "AIM"
            if z == -1:
                welt.blocks[(x,0,z)] = "BEDROCK"
                welt.blocks[(x,2,z)] = "BEDROCK"
            if z == 29 or z == -5 or x == -21 or x == 21:
                welt.blocks[(x,-1,z)] = "BEDROCK"
                welt.blocks[(x,0,z)] = "BEDROCK"
                welt.blocks[(x,1,z)] = "BEDROCK"
            if z < 6:
                welt.blocks[(x,-1,z)] = "BEDROCK"

    welt.blocks[(0,0,-1)] = "DOORBOTTOM"
    welt.blocks[(0,1,-1)] = "DOORTOP"
