import time
import sys
sys.path.append("..")
import interface

def display(f,xmax=80,zmax=None):
    if zmax == None:
        zmax = xmax
    b = interface.Blockworld()

    b.set_pos((0,10,0))

    for x in range(-xmax,xmax+1):
        for z in range(-zmax,zmax+1):
            yt = int(f(x,z))
            yn = min([int(f(x+dx,z+dz)) for dx in (-1,1) for dz in (-1,1)])
            for y in range(yn+1,yt)+[yt]:
                b.set_block((x,y,z),0)

    while b.is_init():
        time.sleep(0.1)
        vx,vy,vz = b.get_sight_vector()
        dx,dy,dz = 0,0,0
        p = b.get_pressed()
        if "w" in p:
            dx = vx; dz = vz
        if "s" in p:
            dx =-vx; dz =-vz
        if "space" in p:
            dy += 1
        if "shift" in p:
            dy -= 1
        b.set_pos(map(sum,zip(b.get_pos(),(dx,dy,dz))))