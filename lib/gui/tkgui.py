#* encoding:utf-8 *#

import sys, os
if __name__ == "__main__":
	sys.path.append(os.path.abspath(".."))
	__package__ = "gui"

import sys, time
if sys.version < "3":
    import Tkinter
    import thread
else:
    import tkinter as Tkinter
    import _thread as thread

from . import filedialog

class GUI(object):
    def __init__(self, config, worldtypes = (), clienttypes = (), background = True):
        if background:
            thread.start_new_thread(self.init,(config,worldtypes,clienttypes))
        else:
            self.init(config,worldtypes,clienttypes)

    def init(self, config, worldtypes, clienttypes):
        self.queue = {}
        self.stats = {}
        self.lock = thread.allocate_lock() #lock that shows whether it is save to do window stuff
        # WINDOW
        root = Tkinter.Tk()
        root.title("MCGCraft Server GUI")
        def on_closing():
            config["run"] = False
            config["quit"] = True
            self.lock.acquire() #wait for lock to be available, lock forever because no one will be able to use window once it's destroyed
            root.destroy()
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.protocol("WM_SAVE_YOURSELF", on_closing)
        root.grid_columnconfigure(1,weight=1)
        self.root = root
        self.row = 0

        # Name des Spiels
        def setname(name):
            config["name"] = name
        self.add_label("Name")
        self.add_entry(config["name"], setname)

        # Speicherort
        def setfile(fn, autocorrect=False):
            if fn == config["file"]:
                return
            if not fn.endswith(".mc.zip") and autocorrect:
                fn += ".mc.zip"
            fileentry.delete(0, Tkinter.END)
            fileentry.insert(0,fn)
            fileentry.xview_moveto(1)
            config["file"] = fn
        def file_focus_out(fn):
            if fn:
                setfile(fn)
            fileentry.isempty = fileentry.get() == ""
            if fileentry.isempty:
                fileentry.insert(0,"Welt nicht speichern")
                fileentry.configure(fg="grey")
        def file_focus_in(event):
            if fileentry.isempty:
                fileentry.delete(0, Tkinter.END)
                fileentry.configure(fg=defaultfg)
        self.add_label("Speicherort")
        fileentry = self.add_entry(config["file"], file_focus_out)
        defaultfg = fileentry["fg"]
        fileentry.xview_moveto(1)
        fileentry.bind("<FocusIn>",file_focus_in)
        file_focus_out(None)
        
        def openfile():
            fn = filedialog.open_dialog("")
            if fn != False:
                setfile(fn, False)
        fileopenbutton = Tkinter.Button(root, text="öffnen", command=openfile)
        fileopenbutton.grid(column = 2, row = self.row-1, sticky = Tkinter.W+Tkinter.E)
        def newfile():
            fn = filedialog.save_dialog("")
            if fn != False:
                setfile(fn, True)
        filenewbutton = Tkinter.Button(root, text="neu", command=newfile)
        filenewbutton.grid(column = 3, row = self.row-1, sticky = Tkinter.W+Tkinter.E)

        # Worldtype #http://effbot.org/tkinterbook/optionmenu.htm
        def setworldtype(*args):
            config["worldtype"] = wtvar.get()
        wtvar = Tkinter.StringVar(root)
        wtvar.set(config["worldtype"]) # default value
        wtvar.trace("w",setworldtype)
        if config["worldtype"] not in worldtypes:
            worldtypes = (config["worldtype"],) + tuple(worldtypes)

        self.add_label("Welttyp")
        wtmenu = Tkinter.OptionMenu(root, wtvar, *worldtypes)
        wtmenu.grid(column = 1, row = self.row, sticky = Tkinter.W+Tkinter.E)
        wtmenu.configure(takefocus=1)
        self.row += 1

        # Mob Spawning
        def setmobspawning(*args):
            config["mobspawning"] = bool(mobspawningvar.get())
        mobspawningvar = Tkinter.IntVar(root)
        mobspawningvar.set(config["mobspawning"])
        mobspawningvar.trace("w",setmobspawning)
        self.add_label("Mob Spawning")
        mobspawning_checkbutton = Tkinter.Checkbutton(root, variable = mobspawningvar)
        mobspawning_checkbutton.grid(column = 1, row = self.row, sticky = Tkinter.W)
        self.row += 1
        
        # Whitelist
        def setwhitelist(*args):
            config["whitelist"] = whitelistvar.get()
        whitelistvar = Tkinter.StringVar(root)
        whitelistvar.set(config["whitelist"])
        whitelistvar.trace("w",setwhitelist)
        self.add_label("Whitelist")
        whitelist_entry = Tkinter.Entry(root, textvariable = whitelistvar)
        whitelist_entry.grid(column = 1, row = self.row, sticky = Tkinter.W+Tkinter.E)
        whitelist_button_local = Tkinter.Radiobutton(text = "localhost", variable = whitelistvar, value = "127.0.0.1")
        whitelist_button_local.grid(column = 2, row = self.row, sticky = Tkinter.W)
        whitelist_button_LAN = Tkinter.Radiobutton(text = "LAN", variable = whitelistvar, value = "192.168.0.0/16")
        whitelist_button_LAN.grid(column = 3, row = self.row, sticky = Tkinter.W)
        self.row += 3

        # Client type
        def setclienttype(*args):
            config["clienttype"] = clienttypevar.get()        
        clienttypevar = Tkinter.StringVar(root)
        clienttypevar.set(config["clienttype"])
        clienttypevar.trace("w",setclienttype)
        
        clienttype_button_desktop = Tkinter.Radiobutton(text = "Desktop", variable = clienttypevar, value = "desktop")
        clienttype_button_desktop.grid(column = 2, row = self.row, sticky = Tkinter.W)
        clienttype_button_web = Tkinter.Radiobutton(text = "Web", variable = clienttypevar, value = "web")
        clienttype_button_web.grid(column = 3, row = self.row, sticky = Tkinter.W)

        if config["clienttype"] not in clienttypes:
            clienttypes = (config["clienttype"],) + tuple(clienttypes)

        self.add_label("Client Type")
        clienttype_menu = Tkinter.OptionMenu(root, clienttypevar, *clienttypes)
        clienttype_menu.grid(column = 1, row = self.row, sticky = Tkinter.W+Tkinter.E)
        clienttype_menu.configure(takefocus=1)
        self.row += 1
        
        # Parole

        # Start/Stop
        def togglerun():
            root.focus()
            config["run"] = not config["run"]
            update_buttontexts()
        startbutton = Tkinter.Button(root, command = togglerun)
        startbutton.grid(column = 1, row = self.row, sticky = Tkinter.W+Tkinter.E)

        # Play
        def play():
            root.focus()
            config["run"] = True
            config["play"] = True
            update_buttontexts()
        playbutton = Tkinter.Button(root, command = play)
        playbutton.grid(column = 2, columnspan = 2, row = self.row, sticky = Tkinter.W+Tkinter.E)
        
        # SAVE?
        
        # BUTTONS
        def update_buttontexts():
            startbutton.configure(text = "Stop" if config["run"] else "Start")
            playbutton.configure(text = "Play" if config["run"] else "Start & Play")
        update_buttontexts()
        self.row += 1
        
        self.statsframe = Tkinter.LabelFrame(root, text="Stats")
        self.statsframe.grid(column = 0, columnspan = 4, row = self.row, sticky = Tkinter.W+Tkinter.E)

        playbutton.focus()
        try:
            while 1:
                time.sleep(0.01)
                root.update()
                while self.queue:
                    name, value = self.queue.popitem()
                    self._set_stats(name,value)
        except:
            pass
    
    def add_entry(self, content, callback):
        def apply_changes(event):
            callback(entry.get())
        entry = Tkinter.Entry(self.root)
        entry.insert(0, content)
        entry.grid(column = 1, row = self.row, sticky = Tkinter.W+Tkinter.E)
        entry.bind("<Return>",apply_changes)
        entry.bind("<FocusOut>",apply_changes)
        self.row += 1
        return entry
    def add_label(self, labeltext):
        Tkinter.Label(self.root, text=labeltext).grid(column = 0, row = self.row, sticky = Tkinter.W)

    def set_stats(self,name,value):
        self.queue[name] = value

    def _set_stats(self,name,value):
        if self.lock.acquire(False): # doing stuff when the window is already closed will block the application, so use lock to avoid destroying root while window get's used
            if not name in self.stats:
                Tkinter.Label(self.statsframe, text=name+" ").grid(column = 0, row = len(self.stats), sticky = Tkinter.W)
                label = Tkinter.Label(self.statsframe)
                label.grid(column = 1, row = len(self.stats), sticky = Tkinter.W)
                self.row += 1
                self.stats[name] = label
            self.stats[name].configure(text = value)
            self.lock.release()

if __name__ == "__main__":
    config = {  "name"     : "MCGCraft Server",
                "file"     : "",
                "worldtype": "Colorland",
                "mobspawning": False,
                "whitelist": "127.0.0.1",
                "clienttype": "desktop",
                "parole"   : "",
                "port"     : "",
                "run"      : False,
                "play"     : False,
                "quit"     : False,
                "save"     : False}
    gui = GUI(config, ("one","two","three"), ("desktop","web"), background = True)
    import time
    time.sleep(1)
    gui.set_stats("fps","16")
