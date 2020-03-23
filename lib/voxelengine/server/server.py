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

import voxelengine.modules.socket_connection_5.socket_connection as socket_connection
import voxelengine.modules.utils
from voxelengine.modules.utils import try_port
from voxelengine.server.players.player import Player

class MyHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """This handler serves files a client might need like texturepack, or in case of webclient the client itself"""
    def __init__(self, texturepack_path, serverinfo, *args, **kwargs):
        self.texturepack_basepath = texturepack_path
        self.serverinfo = serverinfo
        super().__init__(*args, **kwargs)
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
    def translate_path(self, path):
        path = urllib.parse.urlparse(path).path
        path = pathlib.Path(path).relative_to("/")
        if not path.parts:
            raise ValueError("There should be a redirection here")
        elif path.parts[0] == "webclient":
            webclient_relpath = path.relative_to("webclient")
            return os.path.join(VOXELENGINE_PATH, "client", "webtest", str(webclient_relpath))
        elif path.parts[0] == "texturepacks":
            texturepack_relpath = path.relative_to("texturepacks")
            return os.path.join(self.texturepack_basepath, str(texturepack_relpath))
        else:
            return "404.html"
    def log_message(self, format, *args):
        if args[1] == "200":
            return
        super().log_message(format, *args)
        
    def do_HEAD(self):
        path = urllib.parse.urlparse(self.path).path
        path = pathlib.Path(path).relative_to("/")
        if not path.parts:
            #redirection
            host = self.headers.get('Host')
            print(host)
            self.send_response(301)
            self.send_header("Location", "http://mcgcraft.de/webclient/latest/login?server=%s"%host)
            self.end_headers()
        elif path.parts[0] == "info.json":
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.end_headers()
        else:
            super().do_HEAD()
        
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        path = pathlib.Path(path).relative_to("/")
        if not path.parts:
            self.do_HEAD()
        elif path.parts[0] == "info.json":
            self.do_HEAD()
            self.wfile.write(json.dumps(self.serverinfo).encode())
        else:
            super().do_GET()
    


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
        host          : defaults to your IP, only set this if have trouble with automatic detect due to firewall settings or a human readable hostname that resolves to your server and that you want to use

    (bei Benutzung ohne "with", am Ende unbedingt Game.quit() aufrufen)
    """

    def __init__(self,
                 universe,
                 wait=True,
                 name="VoxelengineServer",
                 parole="",
                 texturepack_path=os.path.join(VOXELENGINE_PATH, "texturepacks", "basic_colors",".versions"),
                 PlayerClass=Player,
                 host=None
                 ):
        self.universe = universe
        self.wait = wait
        self.PlayerClass = PlayerClass
        self.host = host or voxelengine.modules.utils.get_ip()

        self.players = {}
        self.new_players = set()
        self._on_disconnect_queue = collections.deque()

        # Serverinfo, ports are added later once they are known
        serverinfo = {
            "name":name,
            "description":"bla",
            }
        # Actual gameplay is done over this connection
        self.game_server = socket_connection.server(on_connect=self._on_connect,
                                                    on_disconnect=self._async_on_disconnect)        
        self.game_port = self.game_server.get_entry_port()
        # Serve texturepack and serverinfo using http
        Handler = functools.partial(MyHTTPHandler, texturepack_path, serverinfo)
        http_port = try_port(80) or try_port(8080) or 0
        self.http_server = http.server.HTTPServer(("", http_port), Handler)
        self.http_thread = threading.Thread(target=self.http_server.serve_forever)
        self.http_thread.start()
        self.http_port = self.http_server.socket.getsockname()[1]
        print("http://%s:%s"%(self.host,self.http_port))
        #
        serverinfo.update({
            "host": self.host,
            "http_port": self.http_port,
            "game_port": self.game_port,
            })
        # 
        self.info_server = socket_connection.beacon(key="voxelgame"+parole,
                                                    info_data=json.dumps(serverinfo))

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
        self.game_server.close()
        self.info_server.close()
        self.http_server.shutdown()
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

    def _async_on_disconnect(self,addr):
        self._on_disconnect_queue.append(addr)
    
    def _on_connect(self,addr):
        """place at worldspawn"""
        if "-debug" in sys.argv:
            print(addr, "connected")
        p = self.PlayerClass(self.universe)
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
        while self._on_disconnect_queue:
            self._on_disconnect(self._on_disconnect_queue.popleft())
        for addr,player in self.players.items():
            for msg in player.outbox:
                self.game_server.send(addr,msg)
                if player.outbox.sentcount >= 0: #test after send, so at least one massage is sent anyway
                    break
        for player in self.get_players():
            player._update() #call to player._update() has to be before call to player._handle_input()
        for msg, addr in self.game_server.receive():
            if addr in self.players:
                self.players[addr]._handle_input(msg)
            else:
                print("Message from unregistered Player")
    
    def launch_client(self, client_type, username="", password=""):
        path = os.path.join(PATH, "..", "client", client_type, "client.py")
        if not os.path.exists(path):
            print("no matching call for selected client type", client_type)
            return
        python = "python" if sys.platform == "win32" else "python3"
        command = [python,
                   path,
                   "%s:%i" % (self.host, self.http_port),
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
