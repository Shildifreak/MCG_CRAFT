import random

def init(welt):
    n = 100
    for x in range(-n,n):
        for z in range(-n,n):
            welt.blocks[(x,0,z)] = random.choice(["GRASS"])

spawnpoint = (0,5,0)

