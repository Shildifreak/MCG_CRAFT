# -*- coding: utf-8 -*-
import math
import random

terrain_generator = []

spawnpoint = (0,10,0)



# Das ist eine Funktion die Bäume erzeugt
def baum(position, size, direction):
    pass

def init(welt):
    n = 10
    for x in range(-n,n):
        for z in range(-n,n):
            y = int(5*math.sin(0.4*x) + 5*math.sin(0.4*z)) + random.randint(-10,11)//10
            welt[(x,y,z)] = "GRASS"
            for dy in range(y-5,y):
                welt[(x,dy,z)] = "DIRT"
            for dy in range(-20,y-5):
                welt[(x,dy,z)] = "STONE"
            welt[(x,-20,z)] = "BEDROCK"
    
    baum((0,0,0), 10, (0,1,0))
    
