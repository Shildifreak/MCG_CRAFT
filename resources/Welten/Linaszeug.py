# -*- coding: cp1252 -*-
terrain_generator = []

spawnpoint = (0,5,0)

def init(welt):
    x = 0
    y = 0
    z = 0
    positionsvector = (x,y,z) 
    welt[positionsvector] = "GRASS"
    welt[(1,0,0)] = "GRASS"
    welt[(0,0,1)] = "GRASS"
    welt[(1,0,1)] = "IRON"
    for x in range(0,112):
        for z in range(o,112):
        welt[(x,0,z)] = "DUNKELGRAU"
        welt[(x,0,z)] = "GRASS"
            
