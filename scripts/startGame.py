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
        self.on_game_start = lambda:None
        self.on_game_exit = lambda:None

    @property
    def running(self):
        return self.game_process and self.game_process.poll() == None

    def start_game(self):
        path = os.path.join(PATH, "..", "mcgcraft.py")
        python = sys.executable
        command = [python, path, serverconfigfn,"--stats-port=%i"%stats_port]
        self.game_process = subprocess.Popen(command,stdin=subprocess.PIPE)

        self.on_game_start()
        def watchdog_thread_function():
            self.game_process.wait()
            self.on_game_exit()
        watchdog_thread = threading.Thread(target=watchdog_thread_function,daemon=False)
        watchdog_thread.start()

    def handle_command(self, command):
        """returns boolean that indicates whether the command worked"""
        if self.running:
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

for pathname in serverconfig["feature_paths"]:
    if pathname not in serverconfig["feature_path_options"]:
        serverconfig["feature_path_options"].append(pathname)
for pathname in os.listdir(os.path.join(PATH,"..","features")):
    if pathname not in serverconfig["feature_path_options"]:
        serverconfig["feature_path_options"].append(pathname)

def get_worldtypes():
    worldtypes = []
    for feature_path in serverconfig["feature_paths"]:
        worldtypes_dir = os.path.join(PATH,"..","features",feature_path,"Welten") #everything before feature_path is dropped in case of absolute path
        if os.path.isdir(worldtypes_dir):
            worldtypes.extend(os.listdir(worldtypes_dir))
    worldtypes = sorted(set([x[:-3] for x in worldtypes if (x.endswith(".py") or x.endswith(".js")) and not x.startswith("_")]))
    return worldtypes

def get_clienttypes():
    clienttypes = os.listdir(os.path.join(PATH,"..","lib","voxelengine","client"))
    clienttypes = [c for c in clienttypes if os.path.exists(os.path.join(PATH, "..", "lib", "voxelengine", "client", c, "client.py"))]
    return clienttypes

ui = UI(serverconfig, clientconfig,
        get_worldtypes, get_clienttypes,
        callback=command_handler.handle_command,
        background=False)
command_handler.on_game_start = lambda:ui.set_running(True)
command_handler.on_game_exit  = lambda:ui.set_running(False)
serverconfig.on_save_callback = lambda:command_handler.handle_command("reload") if command_handler.running else None

ui.mainloop()
command_handler.close()
print("finished")
