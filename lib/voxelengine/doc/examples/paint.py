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
class Player(voxelengine.Player):
    def __init__(self, *args,**kwargs):
        super().__init__(*args,**kwargs)
        self.set_focus_distance(100)

with voxelengine.GameServer(u, PlayerClass=Player) as g:
    g.launch_client("desktop")
    while not g.get_players():
            g.update()
            time.sleep(0.5) #wait for players to connect
    while g.get_players():
        g.update()
        u.tick()
        for player in g.get_players():
            if player.was_pressed("left click"):
                print("aha")
                focused_block = player.entity.get_focused_pos(100)[1]
                if focused_block:
                    if w[focused_block] == "GREEN":
                        w[focused_block] = "BLACK"
                    else:
                        w[focused_block] = "GREEN"
#w.save("picture.zip")
