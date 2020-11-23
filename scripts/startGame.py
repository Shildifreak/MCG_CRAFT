#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os, inspect
import subprocess
import functools
import ast, json
import socket, threading

PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(os.path.join(PATH,".."))
sys.path.append(os.path.join(PATH,"..","lib"))

from gui.tkgui import ServerGUI as UI
from config import clientconfig, serverconfig, serverconfigfn

clientconfig.enable_autosave()
serverconfig.enable_autosave()

def stats_thread_function():
    global stats_port
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(("localhost",0))
        stats_port = s.getsockname()[1]
        buff = b""
        while True:
            new_data,_ = s.recvfrom(1024)
            buff += new_data
            *msgs, buff = buff.split(b"\n")
            for msg in msgs:
                key, value = json.loads(msg.decode())
                ui.set_stats(key, value)
                
stats_thread = threading.Thread(target=stats_thread_function,daemon=True)
stats_thread.start()

def get_launch_client_command():
    return "play %s %s %s" % (clientconfig["clienttype"], clientconfig["username"], clientconfig["password"])

class CommandHandler(object):
    def __init__(self):
        self.game_process = None

    def start_game(self):
        path = os.path.join(PATH, "..", "mcgcraft.py")
        python = "python" if sys.platform == "win32" else "python3"
        command = [python, path, serverconfigfn,"--stats-port=%i"%stats_port]
        self.game_process = subprocess.Popen(command,stdin=subprocess.PIPE)

    def handle_command(self, command):
        """returns boolean that indicates whether the command worked"""
        if self.game_process and self.game_process.poll() == None:
            if command == "run":
                return False
            else:
                if command == "play":
                    command = get_launch_client_command()
                self.game_process.stdin.write((command+"\n").encode())
                self.game_process.stdin.flush()
                return True
        else:
            if command == "run":
                self.start_game()
                return True
            elif command == "quit":
                pass #silently ignore quit if game isn't running
            else:
                print("cant send command, game is not running")
            return False
    
    def close(self):
        if self.game_process:
            self.game_process.wait()

command_handler = CommandHandler()

worldtypes = []
for resource_path in serverconfig["resource_paths"]:
    worldtypes_dir = os.path.join(PATH,"..","resources",resource_path,"Welten") #everything before resource_path is dropped in case of absolute path
    if os.path.isdir(worldtypes_dir):
        worldtypes.extend(os.listdir(worldtypes_dir))
worldtypes = sorted(set([x[:-3] for x in worldtypes if (x.endswith(".py") or x.endswith(".js")) and not x.startswith("_")]))

clienttypes = os.listdir(os.path.join(PATH,"..","lib","voxelengine","client"))
clienttypes = [c for c in clienttypes if os.path.exists(os.path.join(PATH, "..", "lib", "voxelengine", "client", c, "client.py"))]

ui = UI(serverconfig, clientconfig,
        worldtypes, clienttypes,
        callback=command_handler.handle_command,
        background=False)
ui.mainloop()
command_handler.close()
print("finished")
