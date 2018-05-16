#* encoding: utf-8 *#

import voxelengine
import math, os, time

w = voxelengine.World()

e = voxelengine.Entity()
e.set_world(w,(-1,0,-3))
e["texture"] = "PLAYER"

settings = {"init_function" : w.spawn_player,
            "suggested_texturepack" : "mcgcraft-standart",
            }

with voxelengine.Game(**settings) as g:
    g.launch_client()
    while not g.get_players():
            g.update()
            time.sleep(0.5) #wait for players to connect
    w.set_block((-1,-2,-3),"GRASS")
    i = 0
    while g.get_players():
        i+=1
        g.update()
        e["rotation"] = (2*i,i)
        #e.set_position((-1,math.sin(i)+1,-3),w)
    print w.entities
