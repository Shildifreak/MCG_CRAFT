import random

def init(welt):
    n = 10*10
    for x in range(n):
        for z in range(n):
            welt[(x,int((x-z)/2),z)] = random.choice(["STEIN","GRASS","DIRT"])

terrain_generator = []

spawnpoint = (0,5,0)

