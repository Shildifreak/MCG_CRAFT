#* encoding: utf-8 *#

import voxelengine
import math, os

#voxelengine.load_setup(os.path.join(voxelengine.PATH,"setups","mc_setup.py"))

w = voxelengine.World()

e = voxelengine.Entity()
e.set_world(w,(-1,0,-3))
e["texture"] = "PLAYER"

settings = {"init_function" : w.spawn_player,
                "suggested_texturepack" : "mcgcraft-standart",
                }

with voxelengine.Game(**settings) as g:
    w.set_block((-1,-2,-3),"GRASS")
    i = 0
    while g.get_players():
        i+=1
        g.update()
        e["rotation"] = (2*i,i)
        #e.set_position((-1,math.sin(i)+1,-3),w)
    print w.entities
