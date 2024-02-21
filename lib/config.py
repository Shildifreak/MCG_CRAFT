import sys, os, inspect
import functools
import getpass
import json

PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(os.path.join(PATH,".."))

import voxelengine.modules.appdirs as appdirs

configdir = appdirs.user_config_dir("MCGCraft","ProgrammierAG")
serverconfigfn = os.path.join(configdir,"serversettings.json")
clientconfigfn = os.path.join(configdir,"clientsettings.json")

class Config(dict):
    def __init__(self, fn, *args, **kwargs):
        """fn: filename of file to load from and save to"""
        self.fn = fn
        self.autosave_enabled = False
        self.on_save_callback = None
        super().__init__(*args, **kwargs)
        if self.fn:
            self.load()

    @functools.wraps(dict.__setitem__)
    def __setitem__(self, *args, **kwargs):
        super().__setitem__(*args, **kwargs)
        if self.autosave_enabled:
            self.save()

    def enable_autosave(self):
        self.autosave_enabled = True
    
    def load(self):
        """update from file"""
        if os.path.exists(self.fn):
            try:
                with open(self.fn,"r") as configfile:
                    rememberedconfig = json.load(configfile)
            except json.decoder.JSONDecodeError:
                raise Exception("Invalid JSON in config file %s" % self.fn)
            self.update(rememberedconfig)
            pass

    def save(self):
        """save to file"""
        if not os.path.exists(os.path.dirname(self.fn)):
            os.makedirs(os.path.dirname(self.fn))
        with open(self.fn,"w") as configfile:
            json.dump(self, configfile, indent=4)
        if self.on_save_callback:
            self.on_save_callback()

default_serverconfig = {
            # Exposed via GUI
            "name"       : "%ss MCGCraft Server" %getpass.getuser(),
            "description": "",
            "file"       : "",
            "worldtype"  : "BeispielWelt_Infinity",
            "mobspawning": True,
            "entitylimit": 5,
            "whitelist"  : ["127.0.0.1","host"],
            "parole"     : "",
            "feature_paths": ["essential","default"],
            "feature_path_options": [],
            "gamemode"   : "creative",

            # Hidden
            "auto_create_entities_for_players" : True,
            "autosaveintervall" : None,
            "host"      : "",
            "http_port" : [80, 8080, 0],
            "tps"       : 60,
            "idle_tps"  : 0,
            "nameserver": "index.mcgcraft.de",
            "public"    : False,
}
default_clientconfig = {
            "username"   : "",
            "password"   : "",
            "clienttype" : "desktop",
            "parole"     : "",
            "address"    : "",
            "nameserver" : "index.mcgcraft.de",
}

serverconfig = Config(serverconfigfn, default_serverconfig)
clientconfig = Config(clientconfigfn, default_clientconfig)
