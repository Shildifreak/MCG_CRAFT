#* encoding: utf-8 *#

import voxelengine
import time

# Welt laden/erstellen
w = voxelengine.World(filename="picture.zip")
for x in xrange(-5,6):
    for y in xrange(-5,6):
        if w[(x,y,-8)] == 0:
            w[(x,y,-8)] = "BLACK"

# Initialisierungsfunktion für den Spieler
def init_func(player):
    w.spawn_player(player)
    player.set_focus_distance(100)

with voxelengine.Game(init_func, multiplayer=False,name="Paint") as g:
    while not g.get_players():
            g.update()
            time.sleep(0.5) #wait for players to connect
    while g.get_players():
        g.update()
        for player in g.get_players():
            if player.was_pressed("left click"):
                focused_block = player.get_focused_pos()[0]
                if focused_block:
                    if w[focused_block] == "GREEN":
                        w[focused_block] = "BLACK"
                    else:
                        w[focused_block] = "GREEN"
w.save("picture.zip")
