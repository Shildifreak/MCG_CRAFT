# -*- coding: utf-8 -*-
import random

spawnpoint = (0,5,0)

def init(welt):
    n = 30
    for x in range(-n,n):
        for z in range(-n,n):
            welt.blocks[(x,0,z)] = random.choice(["STONE","GRASS","DIRT"])
