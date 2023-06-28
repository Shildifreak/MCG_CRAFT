# -*- coding: utf-8 -*-
import math
import random

terrain_generator = []

spawnpoint = (0,20,0)



# Das ist eine Funktion die Bäume erzeugt
def baum(position, size, direction):
    pass

def init(welt):
    for x in range(-50,50):
        for z in range(-50,50):
            r=(x**2+z**2)**0.5
            y = int(15*math.cos(r)/(r**0.5+1))
            for dy in range(y-5,y+1):
                welt.blocks[(x,dy,z)] = "SAND"
            for dy in range(-20,y-5):
                welt.blocks[(x,dy,z)] = "GOLD"
            if y < 0:
                for dy in range(y+1,1):
                    welt.blocks[(x,dy,z)] = "GLAS"
            welt.blocks[(x,-20,z)] = "BEDROCK"
    
    baum((0,0,0), 10, (0,1,0))
