from entities.player import Player

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
        init_function : function to call with new players (callback)
        wait          : wait for players to disconnect before leaving with statement
        name          : name of the server

    (bei Benutzung ohne "with", am Ende unbedingt Game.quit() aufrufen)
    """

    def __init__(self,
                 init_function=lambda player:None,
                 wait=True,
                 name="MCG-CRAFT",
                 suggested_texturepack="basic_colors",
                 PlayerClass=Player,
                 ):
        self.init_function = init_function
        self.wait = wait
        self.renderlimit = renderlimit
        self.suggested_texturepack = suggested_texturepack
        self.PlayerClass = PlayerClass

        self.players = {}
        self.new_players = set()

        import socket_connection_2 as socket_connection
        self.socket_server = socket_connection.server(key="voxelgame",on_connect=self._on_connect,
                                                      on_disconnect=self._on_disconnect,name=name)
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

    def _on_connect(self,addr):
        """place at worldspawn"""
        if "-debug" in sys.argv:
            print(addr, "connected")
        initmessages = [("setup",self.suggested_texturepack)]
        p = self.PlayerClass(self.renderlimit,initmessages)
        self.players[addr] = p
        self.new_players.add(p)
        self.init_function(p)

    def _on_disconnect(self,addr):
        if "-debug" in sys.argv:
            print(addr, "disconnected")
        # do something with player
        player = self.players.pop(addr)
        player.quit()

    def update(self):
        """communicate with clients
        call regularly to make sure internal updates are performed"""
        for addr,player in self.players.items():
            for msg in player.outbox:
                self.socket_server.send(msg,addr)
                if player.outbox.sentcount >= 0: #test after send, so at least one massage is sent anyway
                    break
        for player in self.get_players():
            player._update() #call to player._update() has to be before call to player._handle_input()
        for msg, addr in self.socket_server.receive():
            if addr in self.players:
                self.players[addr]._handle_input(msg)
            elif "-debug" in sys.argv:
                print("Message from unregistered Player")
        time.sleep(0.001) #wichtig damit das threading Zeug klappt
    
    def launch_client(self):
        import subprocess
        command = ["python",os.path.join(PATH,"client.py"),"--host=localhost","--port=%i" %self.socket_server.get_entry_port()]
        p = subprocess.Popen(command)

if __name__ == "__main__":
    from world import World
    
    def _simple_terrain_generator(position):
        """a very simple terrain generator -> flat map with checkerboard pattern"""
        if position[1] == -2:
            return "GREEN" if (position[0]+position[2]) % 2 else "CYAN"
        return "AIR"

    w = World(_simple_terrain_generator)
    settings = {"init_function" : w.spawn_player,
                }
    with GameServer(**settings) as g:
        g.launch_client()
        while not g.get_players():
            g.update()
        w.set_block((-1,2,-3),"YELLOW")
