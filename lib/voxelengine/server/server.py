import sys, os, inspect
if __name__ == "__main__":
	sys.path.append(os.path.abspath("../.."))
	__package__ = "voxelengine.server"
# PATH to this file
PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

import subprocess
import collections

import voxelengine.modules.socket_connection_4.socket_connection_4 as socket_connection
from voxelengine.server.players.player import Player

class GameServer(object):
    """
    Ein GameServer Objekt sorgt für die Kommunikation mit dem/den Klienten.
    Bei Mehrbenutzerprogrammen muss jeder Benutzer sich mittels des
    Programms voxelengine/client.py verbinden.

    Es ist empfehlenswert GameServer mit einem with Statement zu benutzen:
    >>> with GameServer(*args,*kwargs) as g:
    >>>     ...

    args (Argumente):
        spawnpoint : (world, (x,y,z)) where to place new players

    kwargs (optionale Argumente):
        wait          : wait for players to disconnect before leaving with statement
        name          : name of the server

    (bei Benutzung ohne "with", am Ende unbedingt Game.quit() aufrufen)
    """

    def __init__(self,
                 wait=True,
                 name="MCG-CRAFT",
                 suggested_texturepack="basic_colors",
                 PlayerClass=Player,
                 ):
        self.wait = wait
        self.suggested_texturepack = suggested_texturepack
        self.PlayerClass = PlayerClass

        self.players = {}
        self.new_players = set()

        self._on_connect_queue = collections.deque()
        self._on_disconnect_queue = collections.deque()
        self.socket_server = socket_connection.server(key="voxelgame",on_connect=self._async_on_connect,
                                                      on_disconnect=self._async_on_disconnect,name=name)
        if "-debug" in sys.argv:
            print("game ready")

    def __del__(self):
        pass

    def __enter__(self):
        """for use with "with" statement"""
        return self

    def __exit__(self,*args):
        """for use with "with" statement"""
        if args == (None,None,None): #kein Fehler aufgetreten
            while self.wait and self.get_players():
                self.update()
        self.quit()
    
    def quit(self):
        """quit the game"""
        self.socket_server.close()
        for player in self.players.values():
            if player:
                player.quit()

    def get_new_players(self):
        """get set of players connected since last call to this function"""
        ret = self.new_players
        self.new_players = set()
        return ret

    def get_players(self):
        """get a list of connected players"""
        return self.players.values()

    def _async_on_connect(self,addr):
        self._on_connect_queue.append(addr)

    def _async_on_disconnect(self,addr):
        self._on_disconnect_queue.append(addr)
    
    def _on_connect(self,addr):
        """place at worldspawn"""
        if "-debug" in sys.argv:
            print(addr, "connected")
        initmessages = [("setup",self.suggested_texturepack)]
        p = self.PlayerClass(initmessages)
        self.players[addr] = p
        self.new_players.add(p)

    def _on_disconnect(self,addr):
        if "-debug" in sys.argv:
            print(addr, "disconnected")
        # do something with player
        player = self.players.pop(addr)
        player.quit()

    def update(self):
        """communicate with clients
        call regularly to make sure internal updates are performed"""
        while self._on_connect_queue:
            self._on_connect(self._on_connect_queue.popleft())
        while self._on_disconnect_queue:
            self._on_disconnect(self._on_disconnect_queue.popleft())
        for addr,player in self.players.items():
            for msg in player.outbox:
                self.socket_server.send(addr,msg)
                if player.outbox.sentcount >= 0: #test after send, so at least one massage is sent anyway
                    break
        for player in self.get_players():
            player._update() #call to player._update() has to be before call to player._handle_input()
        for msg, addr in self.socket_server.receive():
            if addr in self.players:
                self.players[addr]._handle_input(msg)
            elif "-debug" in sys.argv:
                print("Message from unregistered Player")
        #time.sleep(0.001) #wichtig damit das threading Zeug klappt
        #M# threading got improved in python3, hope that fixed this
    
    def launch_client(self, client_type = "desktop"):
        path = os.path.join(PATH, "..", "client", client_type, "client.py")
        if not os.path.exists(path):
            print("no matching call for selected client type", client_type)
            return
        port = self.socket_server.get_entry_port()
        python = "python" if sys.platform == "win32" else "python3"
        command = [python,
                   path,
                   "--host=localhost",
                   "--port=%i" %port
                  ]
        subprocess.Popen(command)

if __name__ == "__main__":
    from voxelengine.server.world import World
    from voxelengine.server.world_data_template import data
    data["block_world"]["generator"] = {
        "name":"Simple Terrain Generator",
        "seed":0,
        "path":"...",
        "code":\
"""
def terrain(position):
    \"""a very simple terrain generator -> flat map with checkerboard pattern\"""
    if position[1] == -2:
        return "GREEN" if (position[0]+position[2]) % 2 else "CYAN"
    return "AIR"
def init(welt):
    pass
spawnpoint = (0,0,0)
"""
    }

    w = World(data)

    w[(-1,1,-3)] = "GREEN"
    with GameServer(**settings) as g:
        #g.launch_client()
        g.launch_client("web")
        while not g.get_players():
            g.update()
        w[(-1,2,-3)] = "YELLOW"
        while g.get_players():
            #w[(-1,3,-3)] = "RED"
            w.tick()
            g.update()
