# -*- coding: cp1252 -*-
terrain_generator = []

spawnpoint = (0,5,0)



# Das ist eine Funktion die Bäume erzeugt
def baum(position, size, direction):
    pass

def init(welt):
    for x in range(-16,16):
        for z in range(-16,16):
            y = 0
            welt[(x,y,z)] = "GRASS"
    
    baum((0,0,0), 10, (0,1,0))
    
