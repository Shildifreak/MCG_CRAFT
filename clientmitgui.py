#! /usr/bin/env python3
# -*- coding: utf-8 -*-

if __name__ != "__main__":
    raise Warning("clientmitgui.py should not be imported")

import sys, os, inspect, time, ast
import tkinter
import subprocess
sys.path.append("lib")
import voxelengine.modules.socket_connection_4.socket_connection_4 as socket_connection
from gui.tkgui import ClientGUI
from voxelengine.modules import appdirs

# PATH to this file
PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

configdir = appdirs.user_config_dir("MCGCraft","ProgrammierAG")
configfn = os.path.join(configdir,"serversettings.py")
print(configfn)

# config
config = {  "parole"   : "",
            "username" : "",
            "password" : "",
            "clienttype": "desktop",
            "address"  : None,
            "quit"     : False,
            "refresh"  : False}

if os.path.exists(configfn):
    with open(configfn,"r") as configfile:
        rememberedconfig = ast.literal_eval(configfile.read())
    config.update(rememberedconfig)
elif not os.path.exists(configdir):
    os.makedirs(configdir)

clienttypes = os.listdir(os.path.join("lib","voxelengine","client"))
gui = ClientGUI(config, clienttypes=clienttypes, background = False)
def run_gui():
    servers = None
    while True:
        parole = config["parole"]
        with socket_connection.server_searcher(key = "voxelgame"+parole) as s:
            config["refresh"] = False
            while config["parole"] == parole and not config["refresh"]:
                if config["quit"] or config["address"]:
                    return
                gui.update()
                new_servers = s.get_servers()
                if new_servers != servers:
                    servers = new_servers
                    gui.show_servers(servers)
run_gui()
gui.quit()

rememberconfig = config.copy()
for key in ("run","play","quit","save","refresh","address"):
    rememberconfig.pop(key, None)
with open(configfn,"w") as configfile:
    configfile.write(repr(rememberconfig))



if config["address"]:
    client_type = config["clienttype"]
    host, port = config["address"]
    parole = config["parole"]
    name = config["username"]
    password = config["password"]

    path = os.path.join(PATH, "lib", "voxelengine", "client", client_type, "client.py")
    if not os.path.exists(path):
        print("no matching call for selected client type", client_type)
    else:
        python = "python" if sys.platform == "win32" else "python3"
        command = [python,
                   path,
                   "--host=%s" %host,
                   "--port=%i" %port,
                   "--parole=%s" %parole,
                   "--name=%s" %name,
                   "--password=%s" %password,
                  ]
        subprocess.run(command)

