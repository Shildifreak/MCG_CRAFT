import interface
import time
import math

b = interface.Blockworld()

def f(x,z):
    x = x/10.
    z = z/10.
    return 10*math.sin(math.sin(x*(2+math.sin(z)/5)/4)*x-math.pi/2)
    return 0

b.set_pos((0,10,0))

for x in range(-80,80):
    for z in range(-20,20):
        for dy in range(-5,0):
            y = int(f(x,z))
            b.set_block((x,y+dy,z),0)

while b.is_init():
    time.sleep(0.1)
    if "up" in b.get_pressed():
        b.set_pos(map(sum,zip(b.get_pos(),b.get_sight_vector())))