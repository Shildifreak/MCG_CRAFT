import sys, os, inspect
if __name__ == "__main__":
	sys.path.append(os.path.abspath("../.."))
	__package__ = "voxelengine.server"
# PATH to this file
PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
VOXELENGINE_PATH = os.path.join(PATH, "..")

import subprocess
import collections, functools
import http.server
import threading
import pathlib, urllib.parse
import json

import voxelengine.modules.socket_connection_4.socket_connection_4 as socket_connection
from voxelengine.modules.utils import try_port
from voxelengine.server.players.player import Player

class MyHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """This handler serves files a client might need like texturepack, or in case of webclient the client itself"""
    def __init__(self, texturepack_path, *args, **kwargs):
        self.texturepack_basepath = texturepack_path
        super().__init__(*args, **kwargs)
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', 'http://mcgcraft.de')
        super().end_headers()
    def translate_path(self, path):
        path = urllib.parse.urlparse(path).path
        path = pathlib.Path(path).relative_to("/")
        if not path.parts:
            return os.path.join(VOXELENGINE_PATH, "client", "webtest", "login.html")
        elif path.parts[0] == "webclient":
            webclient_relpath = path.relative_to("webclient")
            return os.path.join(VOXELENGINE_PATH, "client", "webtest", webclient_relpath)
        elif path.parts[0] == "texturepacks":
            texturepack_relpath = path.relative_to("texturepacks")
            return os.path.join(self.texturepack_basepath, texturepack_relpath)
        else:
            return "404.html"
    def log_message(self, format, *args):
        if args[1] == "200":
            return
        super().log_message(format, *args)
        
class GameServer(object):
    """
    Ein GameServer Objekt sorgt für die Kommunikation mit dem/den Klienten.
    Bei Mehrbenutzerprogrammen muss jeder Benutzer sich mittels des
    Programms voxelengine/client/desktop/client.py verbinden.

    Es ist empfehlenswert GameServer mit einem with Statement zu benutzen:
    >>> with GameServer(*args, **kwargs) as g:
    >>>     ...

    args (Argumente):
        universe      : the universe this server is going to run

    kwargs (optionale Argumente):
        wait          : wait for players to disconnect before leaving with statement
        name          : name of the server
        parole        : some phrase people have to know to find this server (they will always be able to connect if they have the IP)
        texturepack_path : where to find that texturepack that should be used for this server
        PlayerClass   : a subclass of voxelengine.Player ... can be used to do initial stuff for newly joined players
        

    (bei Benutzung ohne "with", am Ende unbedingt Game.quit() aufrufen)
    """

    def __init__(self,
                 universe,
                 wait=True,
                 name="VoxelengineServer",
                 parole="",
                 texturepack_path=os.path.join(VOXELENGINE_PATH, "texturepacks", "basic_colors",".versions"),
                 PlayerClass=Player
                 ):
        self.universe = universe
        self.wait = wait
        self.parole = parole
        self.PlayerClass = PlayerClass

        self.players = {}
        self.new_players = set()

        self._on_connect_queue = collections.deque()
        self._on_disconnect_queue = collections.deque()
        self.socket_server = socket_connection.server(key="voxelgame"+self.parole,on_connect=self._async_on_connect,
                                                      on_disconnect=self._async_on_disconnect,name=name)

        # PATH to this file
        PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        http_port = try_port(80) or try_port(8080) or 0
        
        # just serve index.html from current working directory
        Handler = functools.partial(MyHTTPHandler, texturepack_path)
        self.httpd = http.server.HTTPServer(("", http_port), Handler)
        self.http_thread = threading.Thread(target=self.httpd.serve_forever)
        self.http_thread.start()
        self.http_port = self.httpd.socket.getsockname()[1]
        print("serving files for client on port",self.http_port)

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
        self.httpd.shutdown()
        self.http_thread.join()
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
        setup_src = {"port":self.http_port}
        initmessages = [("setup",json.dumps(setup_src))]
        p = self.PlayerClass(self.universe, initmessages)
        self.players[addr] = p
        self.new_players.add(p)

    def _on_disconnect(self,addr):
        if "-debug" in sys.argv:
            print(addr, "disconnected")
        # do something with player
        player = self.players.pop(addr)
        player.quit()

    def update(self):
        """ communicate with clients """
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
    
    def launch_client(self, client_type, username="", password=""):
        path = os.path.join(PATH, "..", "client", client_type, "client.py")
        if not os.path.exists(path):
            print("no matching call for selected client type", client_type)
            return
        port = self.socket_server.get_entry_port()
        python = "python" if sys.platform == "win32" else "python3"
        command = [python,
                   path,
                   "--host=localhost",
                   "--port=%i" %port,
                   "--http_port=%i" %self.http_port,
                   "--parole=%s" %self.parole,
                   "--name=%s" %username,
                   "--password=%s" %password,

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
