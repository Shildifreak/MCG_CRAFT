# since this file is inside voxelengine folder we need to add path to voxelengine
import sys, os
sys.path.append(os.path.join("..","..",".."))

import math, time
import voxelengine

tppath = os.path.abspath(os.path.join("..", "..", "..", "..", "resources", "texturepacks", "default", ".versions"))

u = voxelengine.Universe()
w = u.new_world()

e = voxelengine.Entity()
e.set_world(w,(-1,0,-3))
e["texture"] = "DAME"

settings = {"universe" : u,
            "texturepack_path" : tppath,
            }

with voxelengine.GameServer(**settings) as g:
    g.launch_client("desktop")
    while not g.get_players():
            g.update()
            time.sleep(0.5) #wait for players to connect
    w[-1,-2,-3] = "GRASS"
    i = 0
    while g.get_players():
        i+=1
        e["rotation"] = (2*i,i)
        e["position"] = (-1, math.sin(i)+1, -3)
        g.update()
        u.tick()
        time.sleep(0.1)
    print(w.entities)
