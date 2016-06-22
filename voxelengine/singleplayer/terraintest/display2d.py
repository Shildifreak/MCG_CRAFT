import math
import pygame

def colorfilter(y):
    ty = (math.atan(y)/math.pi+0.5)*255
    c = int(ty)
    return (c,c,c)

def display(f,xmax=80,zmax=None,fill="dummy"):
    if zmax == None:
        zmax = xmax

    width = (xmax*2+1)
    height = (zmax*2+1)
    window = pygame.display.set_mode((width,height))
    for x in xrange(-xmax,xmax+1):
        for z in xrange(-zmax,zmax+1):
            y = f(x,z)
            color = colorfilter(y)
            window.set_at((x+xmax,z+zmax),color)
    while True:
        if pygame.event.poll().type == pygame.QUIT:
            break
        pygame.display.update()

if __name__ == "__main__":
    display(lambda x,z:0)