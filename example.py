#* encoding: utf-8 *#

import voxelengine
import math, os

voxelengine.load_setup(os.path.join(voxelengine.PATH,"setups","mc_setup.py"))

w = voxelengine.World()

e = voxelengine.Entity()
e.set_position((-1,0,-3),w)
e.set_texture("PLAYER")

with voxelengine.Game(w.spawn_player) as g:
    w.set_block((-1,-2,-3),"GESICHT")
    i = 0
    while g.get_players():
        i+=0.5
        g.update()
        e.set_rotation(-2*i,45*math.sin(0.1*i))
        #e.set_position((-1,math.sin(i)+1,-3),w)
    print w.entities
