import random

def init(welt):
    n = 100
    for x in range(-n,n):
        for z in range(-n,n):
            welt[(x,0,z)] = random.choice(["STEIN","GRASS","DIRT"])

terrain_generator = []

spawnpoint = (0,5,0)nvghghf

