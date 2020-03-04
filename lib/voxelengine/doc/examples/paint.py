# since this file is inside voxelengine folder we need to add path to voxelengine
import sys, os
sys.path.append(os.path.join("..","..",".."))

import voxelengine
import time

# Welt laden/erstellen
u = voxelengine.Universe()
w = u.new_world() #filename="picture.zip"
for x in range(-5,6):
    for y in range(-5,6):
        if w[(x,y,-8)] == "AIR":
            w[(x,y,-8)] = "BLACK"

# Initialisierungsfunktion für den Spieler
def playerFactory(*args,**kwargs):
    player = voxelengine.Player(*args,**kwargs)
    player._set_world(w)
    player.set_focus_distance(100)
    return player

with voxelengine.GameServer(u) as g:
    g.launch_client("desktop","","")
    while not g.get_players():
            g.update()
            time.sleep(0.5) #wait for players to connect
    while g.get_players():
        g.update()
        #for player in g.get_players():
        #    if player.was_pressed("left click"):
        #        focused_block = player.get_focused_pos()[0]
        #        if focused_block:
        #            if w[focused_block] == "GREEN":
        #                w[focused_block] = "BLACK"
        #            else:
        #                w[focused_block] = "GREEN"
#w.save("picture.zip")
