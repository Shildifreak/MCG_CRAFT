# -*- coding: utf-8 -*-
import math
import random

spawnpoint = (0,10,0)

def init(welt):
    y=0 
    for x in range(0, 10):
        for z in range(0, 10):
            welt.blocks[(x,y,z)] = "GRASS"      

    y=-1
    for i in range(0, 7):
        for x in range(0, 10):
            for z in range(0, 10):
                welt.blocks[(x,y,z)] = "DIRT"      
        y=y-1
                
