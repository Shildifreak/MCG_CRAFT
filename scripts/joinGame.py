#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os, inspect, time, ast
import tkinter
import subprocess
import json
import collections

# LIBPATH to folder containing voxelengine
PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
LIBPATH = os.path.join(PATH, "..", "lib")
sys.path.append(LIBPATH)

import voxelengine.modules.socket_connection_5.socket_connection as socket_connection
from gui.tkgui import ClientGUI
from gui.config import clientconfig
from voxelengine.modules import appdirs

clienttypes = os.listdir(os.path.join(LIBPATH,"voxelengine","client"))
clienttypes = [c for c in clienttypes if os.path.exists(os.path.join(LIBPATH, "voxelengine", "client", c, "client.py"))]

events = collections.defaultdict(bool)
def callback(command, value=True):
    events[command] = value
        
gui = ClientGUI(None, clientconfig, clienttypes=clienttypes, callback=callback, background = False)
def run_gui():
    servers = None
    while True:
        parole = clientconfig["parole"]
        with socket_connection.server_searcher(key = "voxelgame"+parole) as s:
            events.clear()
            while clientconfig["parole"] == parole and not events["refresh"]:
                if events["quit"] or events["address"]:
                    return
                gui.update()
                new_servers = list(map(json.loads, s.get_servers()))
                if new_servers != servers:
                    servers = new_servers
                    gui.show_servers(servers)
run_gui()
gui.quit()

clientconfig.save()

if events["address"]:
    address = events["address"]
    client_type = clientconfig["clienttype"]
    name = clientconfig["username"]
    password = clientconfig["password"]

    path = os.path.join(LIBPATH, "voxelengine", "client", client_type, "client.py")
    if not os.path.exists(path):
        print("no matching call for selected client type", client_type)
    else:
        python = "python" if sys.platform == "win32" else "python3"
        command = [python,
                   path,
                   address,
                   "--name=%s" %name,
                   "--password=%s" %password,
                  ]
        subprocess.run(command)

