#* encoding: utf-8 *#

import voxelengine

w = voxelengine.World(filename="picture.zip")

with voxelengine.Game( spawnpoint=(w,(0,0,0)) ) as g:
    for x in xrange(-5,6):
        for y in xrange(-5,6):
            if w[(x,y,-8)] == 0:
                w[(x,y,-8)] = "SCHWARZ"
    while g.get_players():
        g.update()
        for player in g.get_new_players():
            print player
            player.set_focus_distance(100)
        for player in g.get_players():
            if player.was_pressed("left click"):
                focused_block = player.get_focused_pos()[0]
                if focused_block:
                    if w.get_block_name(focused_block) == "GRUN":
                        w[focused_block] = "SCHWARZ"
                    else:
                        w[focused_block] = "GRUN"
w.save("picture.zip")