import math
import random
import copy

spawnpoint = (5,10,5)

n = 10

def init(welt):
    array = n**2*[1]

    for x in range(n):
        for z in range(n):
            array[index(x,z)] = (((x-4.5)**2 + (z-4.5)**2)**0.5) < 5


    y = 0
    while sum(array):
        for x in range(n):
            for z in range(n):
                if array[index(x,z)]>0.1:
                    welt.blocks[(x,y,z)] = "GRASS" if y == 0 else "ROSA"
        y -= 1
        array = step(array,-y)

def step(array,y):
    new_array = copy.copy(array)
    for x in range(n):
        for z in range(n):
            i1 = index(x,z)
            if i1 != None:
                i2s = []
                for dx in (-1,0,1):
                    for dz in (-1,0,1):
                        i2 = index(x+dx,z+dz)
                        if i2 != None and array[i2] >= array[i1]:
                            i2s.append(i2)
                if i2s:
                    c = random.random()
                    w = c/len(i2s)
                    for i2 in i2s:
                        new_array[i2] += array[i1]*w
                    new_array[i1] -= c*array[i1]
    for x in range(n):
        for z in range(n):
            i = index(x,z)
            new_array[i] -= min(0.01*y, new_array[i])
    return new_array

def index(x, y):
    if 0 <= x < n:
        if 0 <= y < n:
            return x*n+y
    return None

if __name__ == "__main__":
    array = n**2*[1]

    for x in range(n):
        for z in range(n):
            array[index(x,z)] = (((x-4.5)**2 + (z-4.5)**2)**0.5) < 5

    y = 0
    while sum(array):
        print(sum(array))
        if True:
            for x in range(n):
                for z in range(n):
                    e = array[index(x,z)]
                    #e = round(e,0)
                    e = "x" if e > 0.1 else " "
                    print(e,end="")                    
                print()
        y += 1
        array = step(array,y)
        input()

6
