# -*- coding: utf-8 -*-
import math
import random

spawnpoint = (0,10,0)

def init(welt):
    n = 5
    for x in range(-n,n):
        for z in range(-n,n):
            y = int(5*math.sin(0.4*x) + 5*math.sin(0.4*z)) + random.randint(-10,11)//10
            welt.blocks[(x,y,z)] = "SAND"
            for dy in range(y-5,y):
                welt.blocks[(x,dy,z)] = "SANDSTEIN"
            for dy in range(-20,y-5):
                welt.blocks[(x,dy,z)] = "STONE"
            welt.blocks[(x,-20,z)] = "BEDROCK"
