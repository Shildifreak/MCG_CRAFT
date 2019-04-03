# -*- coding: cp1252 -*-
import math
import random

terrain_generator = []

spawnpoint = (0,10,0)



# Das ist eine Funktion die Bäume erzeugt
def baum(position, size, direction):
    pass

def init(welt):
    for x in range(-50,50):
        for z in range(-50,50):
            y = int(5*math.sin((0.3+random.random()/5)*x) + 5*math.sin((0.3+random.random()/5)*z))
            welt[(x,y,z)] = "GRASS"
            for dy in range(y-5,y):
                welt[(x,dy,z)] = "DIRT"
            for dy in range(-20,y-5):
                welt[(x,dy,z)] = "STONE"
            welt[(x,-20,z)] = "BEDROCK"
    
    baum((0,0,0), 10, (0,1,0))
    
