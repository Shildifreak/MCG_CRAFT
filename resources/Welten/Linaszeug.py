# -*- coding: utf-8 -*-

spawnpoint = (0,5,0)

def init(welt):
    x = 0
    y = 0
    z = 0
    positionsvector = (x,y,z) 
    welt.blocks[positionsvector] = "GRASS"
    welt.blocks[(1,0,0)] = "GRASS"
    welt.blocks[(0,0,1)] = "GRASS"
    welt.blocks[(1,0,1)] = "IRON"
    for x in range(0,112):
        for z in range(0,112):
            welt.blocks[(x,0,z)] = "DUNKELGRAU"
            welt.blocks[(x,0,z)] = "GRASS"
            
