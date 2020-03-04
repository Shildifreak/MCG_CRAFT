# -*- coding: utf-8 -*-
import math
import random
import tree

spawnpoint = (3,8,3)

def insel(welt,x,y,h,r):
    if random.random() < 0.1:
        wuste = True
        rv = [2,7,0.3,0,0]
        baumtyp="kaktus"
    else:
        wuste = False
        rv = [2,7,1.5,0.1,0.03]
        baumtyp="eiche"
    
    dr = 0.625

    trees = random.random() < 0.5

    
    
    for a in range(x-int(1.5*r), x+int(1.5*r)):
        for b in range(y-int(1.5*r), y+int(1.5*r)):
            if ((a-x)**2+(b-y)**2)**0.5 < r+(random.choices([-1,0,1,2,3],rv)[0]):
                if wuste:
                    welt.blocks[(a,h,b)] = "SAND"
                else:
                    welt.blocks[(a,h,b)] = "GRASS"      

    
    for i in range(-2, 100):
        for a in range(x-int(1.5*r), x+int(1.5*r)):
            for b in range(y-int(1.5*r), y+int(1.5*r)):
                if i < 1:
                    if ((a-x)**2+(b-y)**2)**0.5 < r+(random.choices([-1,0,1,2,3],rv)[0])+5*dr*(i-1):
                        if welt.blocks[(a,h+1-i,b)] == "AIR":
                            if wuste:
                                welt.blocks[(a,h-i,b)] = "SAND"
                            else:
                                welt.blocks[(a,h-i,b)] = "GRASS"
                        else:
                            if wuste:
                                welt.blocks[(a,h-i,b)] = "SAND"
                            else:
                                welt.blocks[(a,h-i,b)] = "DIRT"
                            
                else:
                    if welt.blocks[(a,h+1-i,b)] == "AIR":
                        if ((a-x)**2+(b-y)**2)**0.5 < r+(random.choices([-1,0,1,2,3],rv)[0])-dr*i:
                            if i<4:
                                if wuste:
                                    welt.blocks[(a,h-i,b)] = "SAND"
                                else:
                                    welt.blocks[(a,h-i,b)] = "GRASS"
                            elif random.random() < 0.3:
                                if wuste:
                                    welt.blocks[(a,h-i,b)] = "SAND"
                                else:
                                    welt.blocks[(a,h-i,b)] = "GRASS"
                            else:
                                if wuste:
                                    welt.blocks[(a,h-i,b)] = "SANDSTEIN"
                                else:
                                    welt.blocks[(a,h-i,b)] = "STONE"
                    elif ((a-x)**2+(b-y)**2)**0.5 < r+(random.choices([-1,0,1,2,3],rv)[0])-dr*i:
                        if wuste:
                            if welt.blocks[(a,h+1-i,b)] == "SAND":
                                if random.random() < 0.65:
                                    welt.blocks[(a,h-i,b)] = "SAND"
                                else:
                                    welt.blocks[(a,h-i,b)] = "SANDSTEIN"
                            else:
                                welt.blocks[(a,h-i,b)] = "SANDSTEIN"
                        else:
                            if welt.blocks[(a,h+1-i,b)] == "GRASS":
                                if random.random() < 0.95:
                                    welt.blocks[(a,h-i,b)] = "DIRT"
                                elif random.random() < 0.1:
                                    welt.blocks[(a,h-i,b)] = "STONE"
                                else:
                                    welt.blocks[(a,h-i,b)] = "MOSSSTONE"
                            elif welt.blocks[(a,h+2-i,b)] == "GRASS" and welt.blocks[(a,h+1-i,b)] == "DIRT":
                                if random.random() < 0.40:
                                    welt.blocks[(a,h-i,b)] = "DIRT"
                                elif random.random() < 0.5:
                                    welt.blocks[(a,h-i,b)] = "STONE"
                                else:
                                    welt.blocks[(a,h-i,b)] = "MOSSSTONE"
                            elif welt.blocks[(a,h+1-i,b)] == "DIRT":
                                if random.random() < 0.10:
                                    welt.blocks[(a,h-i,b)] = "DIRT"
                                elif random.random() < 0.55:
                                    welt.blocks[(a,h-i,b)] = "STONE"
                                else:
                                    welt.blocks[(a,h-i,b)] = "MOSSSTONE"
                            else:
                                if random.random() < 0.05:
                                    welt.blocks[(a,h-i,b)] = "DIRT"
                                elif random.random() < 0.6:
                                    welt.blocks[(a,h-i,b)] = "STONE"
                                else:
                                    welt.blocks[(a,h-i,b)] = "MOSSSTONE"
                    elif welt.blocks[(a,h+1-i,b)] == "SAND":
                        welt.blocks[(a,h-i,b)] = "SANDSTEIN"
    
    if trees:
        for i in range(int(r**2 / random.randint(15,40))):
            works = False
            while not works:
                a = random.randint(x-r,x+r)
                b = random.randint(y-r,y+r)
                if ((a-x)**2+(b-y)**2)**0.5 < r-2:
                    works = True
         
            for d_pos, block in tree.tree_structure(baumtyp):
                dx, dy, dz = d_pos
                welt.blocks[(a+dx,h+dy,b+dz)] = block
def tempel(welt,x,y,h):
    #x->4
    #y->4
    for i in range(0,5):
        welt.blocks[(x-4,h+i,y-4)]= "STONE"
        welt.blocks[(x+5,h+i,y-4)]= "STONE"
        welt.blocks[(x-4,h+i,y+5)]= "STONE"
        welt.blocks[(x+5,h+i,y+5)]= "STONE"

    welt.blocks[(x-3,h+4,y-3)]= "STONE"
    welt.blocks[(x-4,h+4,y-3)]= "STONE"
    welt.blocks[(x-3,h+4,y-4)]= "STONE"
    welt.blocks[(x+4,h+4,y-3)]= "STONE"
    welt.blocks[(x+4,h+4,y-4)]= "STONE"
    welt.blocks[(x+5,h+4,y-3)]= "STONE"
    welt.blocks[(x-3,h+4,y+4)]= "STONE"
    welt.blocks[(x-3,h+4,y+5)]= "STONE"
    welt.blocks[(x-4,h+4,y+4)]= "STONE"
    welt.blocks[(x+5,h+4,y+4)]= "STONE"
    welt.blocks[(x+4,h+4,y+5)]= "STONE"
    welt.blocks[(x+4,h+4,y+4)]= "STONE"

    
    for dx in range(x-4,x+6):
        for dy in range(y-4,y+6):
            welt.blocks[(dx,h+5,dy)]= "STONE"

    for dx in range(x-2,x+4):
        for dy in range(y-2,y+4):
            welt.blocks[(dx,h+6,dy)]= "STONE"    
    
    for dx in range(x-1,x+3):
        for dy in range(y-1,y+3):
            welt.blocks[(dx,h+7,dy)]= "STONE"
    
    for dx in range(x-5,x+7):
        welt.blocks[(dx,h+4,y-5)]= "STONE"
        welt.blocks[(dx,h+4,y+6)]= "STONE"
    for dy in range(y-5,y+7):
        welt.blocks[(x-5,h+4,dy)]= "STONE"
        welt.blocks[(x+6,h+4,dy)]= "STONE"

    
def init(welt):
    
    insel(welt,6,-6,0,15)
    tempel(welt,6,-6,1)
    for i in range(0,20):
        insel(welt,random.randint(-60,50),random.randint(-40,50),random.randint(-60,20),random.randint(3,15))
    welt.blocks[(0,1,0)] = "HALM"
