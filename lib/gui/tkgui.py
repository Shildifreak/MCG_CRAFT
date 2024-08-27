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
from .tkscroll import VerticalScrolledFrame

import collections
import traceback

from voxelengine.modules.serializableCollections import extended_literal_eval

class GUI(object):
    def __init__(self, serverconfig, clientconfig,
                 get_worldtypes = lambda:(), get_clienttypes = lambda:(),
                 callback = print, background = True):
        self.queue = collections.OrderedDict()
        self.stats = collections.OrderedDict()
        self.lock = thread.allocate_lock() #lock that shows whether it is save to do window stuff
        self.closed = False
        self.disabled_when_running = []
        self.running = False

        self.serverconfig = serverconfig
        self.clientconfig = clientconfig
        self.get_worldtypes = get_worldtypes
        self.clienttypes = get_clienttypes()
        self.callback = callback
        
        if background:
            thread.start_new_thread(self.background_thread,())
        else:
            self.create_window()
            self.init_widgets()

    def background_thread(self):
        self.create_window()
        self.init_widgets()
        self.mainloop()

    def init_widgets(self):
        print("Please overwrite init_widgets method of baseclass GUI and invoke some addwidget_... methods")
    
    def mainloop(self):
        while not self.closed:
            time.sleep(0.01)
            self.update()

    def update(self):
        self.root.update()
        while self.queue:
            id, (func, args) = self.queue.popitem(last=False)
            func(*args)

    def quit(self):
        self.callback("quit")
        self.lock.acquire() #wait for lock to be available, lock forever because destroyed window will never come back
        self.closed = True
        try:
            self.root.destroy()
        except:
            pass

    def create_window(self):
        # WINDOW
        root = Tkinter.Tk()
        root.title("MCGCraft Server GUI")
        def on_closing():
            self.quit()
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.protocol("WM_SAVE_YOURSELF", on_closing)
        root.grid_columnconfigure(1,weight=1)
        self.root = root
        self.row = 0
        
    def addwidgets_name(self):
        # Name des Spiels
        def setname(name):
            self.serverconfig["name"] = name
        self.add_label("Name")
        e = self.add_entry(self.serverconfig["name"], setname)
        self.disabled_when_running.append(e)

    def addwidgets_file(self):
        # Speicherort
        def setfile(fn, autocorrect=False):
            if fn == self.serverconfig["file"]:
                return
            if not fn.endswith(".mc.txt") and autocorrect:
                fn += ".mc.txt"
            fileentry.delete(0, Tkinter.END)
            fileentry.insert(0,fn)
            fileentry.xview_moveto(1)
            self.serverconfig["file"] = fn
            if fn:
                fileentry.configure(fg=defaultfg)
            self.update_worldtypes()
        def setfile_from_entry(*_):
            fn = fileentry.get()
            setfile(fn)
        def file_focus_out(_):
            setfile_from_entry()
            if not self.serverconfig["file"]:
                fileentry.insert(0,"Welt nicht speichern")
                fileentry.configure(fg="grey")
        def file_focus_in(event):
            if not self.serverconfig["file"]:
                fileentry.delete(0, Tkinter.END)
                fileentry.configure(fg=defaultfg)
        self.add_label("Speicherort")
        fileentry = self.add_entry(self.serverconfig["file"], lambda _:None)
        defaultfg = fileentry["fg"]
        fileentry.xview_moveto(1)
        fileentry.bind("<Return>",setfile_from_entry)
        fileentry.bind("<FocusOut>",file_focus_out)
        fileentry.bind("<FocusIn>",file_focus_in)
        file_focus_out(None)
        
        def openfile():
            fn = filedialog.open_dialog(os.path.join("saves","worlds"))
            if fn != False:
                setfile(fn, False)
        fileopenbutton = Tkinter.Button(self.root, text="öffnen", command=openfile)
        fileopenbutton.grid(column = 2, row = self.row-1, sticky = Tkinter.W+Tkinter.E)
        def newfile():
            fn = filedialog.save_dialog(os.path.join("saves","worlds"))
            if fn != False:
                setfile(fn, True)
        filenewbutton = Tkinter.Button(self.root, text="neu", command=newfile)
        filenewbutton.grid(column = 3, row = self.row-1, sticky = Tkinter.W+Tkinter.E)
        self.disabled_when_running.append(fileopenbutton)

    def addwidgets_autosave(self):
        # Autosave
        def setautosave(*args):
            self.serverconfig["autosaveintervall"] = autosavevar.get()
            if self.serverconfig["autosaveintervall"]:
                autosave_entry.configure(state="normal")
            else:
                autosave_entry.configure(state="disabled")
        autosavevar = Tkinter.IntVar(self.root)
        autosavevar.trace("w",setautosave)
        def only_numbers(char):
            return char.isdigit()
        validation = self.root.register(str.isdigit) # Register func
        autosave_entry = Tkinter.Entry(self.root, 
            textvariable = autosavevar, 
            validate="key", 
            validatecommand=(validation, '%P'),
            )
        autosave_entry.grid(column = 2, row = self.row, sticky = Tkinter.W)
        self.add_label("Autosave")
        autosave_checkbutton = Tkinter.Checkbutton(self.root, variable = autosavevar, onvalue = 300)
        autosave_checkbutton.grid(column = 1, row = self.row, sticky = Tkinter.W)
        autosavevar.set(int(self.serverconfig["autosaveintervall"] or 0))
        self.row += 1

    def addwidgets_worldtype(self):
        # Worldtype #http://effbot.org/tkinterbook/optionmenu.htm
        def setworldtype(*args):
            self.serverconfig["worldtype"] = self.wtvar.get()
            if self.serverconfig["worldtype"] not in self.worldtypes:
                self.wtmenu.configure(foreground="orange red", activeforeground="orange red")
            else:
                self.wtmenu.configure(foreground="black", activeforeground="black")

        self.wtvar = Tkinter.StringVar(self.root)

        self.add_label("Welttyp")
        self.wtmenu = Tkinter.OptionMenu(self.root, self.wtvar, "placeholder")

        self.update_worldtypes()
        self.wtvar.set(self.serverconfig["worldtype"]) # default value
        self.wtvar.trace("w",setworldtype)

        self.wtmenu.grid(column = 1, row = self.row, sticky = Tkinter.W+Tkinter.E)
        self.wtmenu.configure(takefocus=1)
        self.row += 1
    
    def update_worldtypes(self):
        if not self.running:
            if os.path.exists(self.serverconfig["file"]):
                try:
                    with open(self.serverconfig["file"]) as f:
                        c = f.read()
                    ignore_custom_nodes = collections.defaultdict(lambda:(lambda*a,**kw:None))
                    data = extended_literal_eval(c, ignore_custom_nodes)
                    worldtype = data[0]["block_world"]["generator"]["name"]
                except Exception as e:
                    traceback.print_exc()
                    worldtype = "error"
                self.wtvar.set(worldtype)
                self.wtmenu.configure(state="disabled")
            else:
                self.wtmenu.configure(state="normal")
        else:
            self.wtmenu.configure(state="disabled")
        self.worldtypes = self.get_worldtypes()
        if self.serverconfig["worldtype"] not in self.worldtypes:
            self.wtmenu.configure(foreground="orange red", activeforeground="orange red")
        else:
            self.wtmenu.configure(foreground="black", activeforeground="black")

        self.wtmenu["menu"].delete(0,"end")
        for wt in self.worldtypes:
            self.wtmenu["menu"].add_command(label=wt, command=Tkinter._setit(self.wtvar, wt))

    def addwidgets_mobspawning(self):
        # entity Limit
        def setentitylimit(*args):
            self.serverconfig["entitylimit"] = entitylimitvar.get()
        entitylimitvar = Tkinter.IntVar(self.root)
        entitylimitvar.set(self.serverconfig["entitylimit"])
        entitylimitvar.trace("w",setentitylimit)
        def only_numbers(char):
            return char.isdigit()
        validation = self.root.register(str.isdigit) # Register func
        entitylimit_entry = Tkinter.Entry(self.root, 
            textvariable = entitylimitvar, 
            validate="key", 
            validatecommand=(validation, '%P'),
            )
        entitylimit_entry.grid(column = 2, row = self.row, sticky = Tkinter.W)
        # Mob Spawning
        def setmobspawning(*args):
            self.serverconfig["mobspawning"] = bool(mobspawningvar.get())
            if self.serverconfig["mobspawning"]:
                entitylimit_entry.configure(state="normal")
            else:
                entitylimit_entry.configure(state="disabled")
        mobspawningvar = Tkinter.IntVar(self.root)
        mobspawningvar.trace("w",setmobspawning)
        mobspawningvar.set(self.serverconfig["mobspawning"])
        self.add_label("Mob Spawning")
        mobspawning_checkbutton = Tkinter.Checkbutton(self.root, variable = mobspawningvar)
        mobspawning_checkbutton.grid(column = 1, row = self.row, sticky = Tkinter.W)
        self.row += 1
    
    def addwidgets_gamemode(self):
        # Client type
        def setgamemode(*args):
            self.serverconfig["gamemode"] = gamemodevar.get()        
        gamemodevar = Tkinter.StringVar(self.root)
        gamemodevar.set(self.serverconfig["gamemode"])
        gamemodevar.trace("w",setgamemode)
        
        gamemode_button_creative = Tkinter.Radiobutton(text = "Creative", variable = gamemodevar, value = "creative")
        gamemode_button_creative.grid(column = 1, row = self.row, sticky = Tkinter.W)
        gamemode_button_survival = Tkinter.Radiobutton(text = "Survival", variable = gamemodevar, value = "survival")
        gamemode_button_survival.grid(column = 2, row = self.row, sticky = Tkinter.W, columnspan = 2)

        self.add_label("Gamemode")
        self.row += 1
        
    def addwidgets_whitelist(self):
        # Whitelist
        def setwhitelist(*args):
            self.serverconfig["whitelist"] = whitelistvar.get().replace(" ","").split(",")
        whitelistvar = Tkinter.StringVar(self.root)
        whitelistvar.set(",".join(self.serverconfig["whitelist"]))
        whitelistvar.trace("w",setwhitelist)
        self.add_label("Whitelist")
        whitelist_entry = Tkinter.Entry(self.root, textvariable = whitelistvar)
        whitelist_entry.grid(column = 1, row = self.row, sticky = Tkinter.W+Tkinter.E)
        whitelist_button_local = Tkinter.Radiobutton(text = "This PC", variable = whitelistvar, value = "127.0.0.1,host")
        whitelist_button_local.grid(column = 2, row = self.row, sticky = Tkinter.W)
        whitelist_button_LAN = Tkinter.Radiobutton(text = "LAN", variable = whitelistvar, value = "192.168.0.0/16,10.0.0.0/8,127.0.0.1")
        whitelist_button_LAN.grid(column = 3, row = self.row, sticky = Tkinter.W)
        self.row += 3
        self.disabled_when_running.extend([whitelist_entry, whitelist_button_local, whitelist_button_LAN])

    def addwidgets_server_parole(self):
        # Parole
        def setparole(parole):
            self.serverconfig["parole"] = parole
        self.add_label("Parole")
        e = self.add_entry(self.serverconfig["parole"], setparole)
        self.disabled_when_running.append(e)

    def addwidgets_client_parole(self):
        # Parole
        def setparole(parole):
            self.clientconfig["parole"] = parole
        self.add_label("Parole")
        self.add_entry(self.clientconfig["parole"], setparole)

    def addwidgets_username_password(self):
        # Username
        def setusername(username):
            if self.clientconfig["username"] != username:
                self.clientconfig["username"] = username
            if username:
                self.passwordlabel.grid()
                self.passwordentry.grid()
            else:
                self.passwordlabel.grid_remove()
                self.passwordentry.grid_remove()
                
        self.add_label("Username")
        self.add_entry(self.clientconfig["username"], setusername)

        # Password
        def setpassword(password):
            self.clientconfig["password"] = password
        self.passwordlabel = self.add_label("Password")
        self.passwordentry = self.add_entry(self.clientconfig["password"], setpassword)

        setusername(self.clientconfig["username"])

    def addwidgets_clienttype(self):
        # Client type
        def setclienttype(*args):
            self.clientconfig["clienttype"] = clienttypevar.get()        
        clienttypevar = Tkinter.StringVar(self.root)
        clienttypevar.set(self.clientconfig["clienttype"])
        clienttypevar.trace("w",setclienttype)
        
        clienttype_button_desktop = Tkinter.Radiobutton(text = "Desktop", variable = clienttypevar, value = "desktop")
        clienttype_button_desktop.grid(column = 2, row = self.row, sticky = Tkinter.W)
        clienttype_button_web = Tkinter.Radiobutton(text = "Web", variable = clienttypevar, value = "web")
        clienttype_button_web.grid(column = 3, row = self.row, sticky = Tkinter.W)

        if self.clientconfig["clienttype"] not in self.clienttypes:
            self.clienttypes = (self.clientconfig["clienttype"],) + tuple(self.clienttypes)

        self.add_label("Client Type")
        clienttype_menu = Tkinter.OptionMenu(self.root, clienttypevar, *self.clienttypes)
        clienttype_menu.grid(column = 1, row = self.row, sticky = Tkinter.W+Tkinter.E)
        clienttype_menu.configure(takefocus=1)
        self.row += 1
        

    def addwidgets_featurepaths(self):
        self.add_label("Features")
        featurepaths_menubutton = Tkinter.Menubutton(self.root, relief="raised")
        featurepaths_menubutton["menu"] = featurepaths_menu = Tkinter.Menu(featurepaths_menubutton, tearoff=0)
        
        def update_text():
            featurepaths_menubutton.configure(
                text=", ".join(p.split("/")[-1] for p in self.serverconfig["feature_paths"]) or "nothing selected",
                foreground="black", activeforeground="black")
            if not "essential" in self.serverconfig["feature_paths"]:
                featurepaths_menubutton.configure(foreground="orange red", activeforeground="orange red")
        update_text()
        
        def update_selection(feature_path, v):
            enabled = v.get()
            if enabled:
                if feature_path in self.serverconfig["feature_paths"]:
                    return
                self.serverconfig["feature_paths"].append(feature_path)
            else:
                if not feature_path in self.serverconfig["feature_paths"]:
                    return
                self.serverconfig["feature_paths"].remove(feature_path)
            update_text()
            self.serverconfig["feature_paths"] = self.serverconfig["feature_paths"] # to trigger save
            self.update_worldtypes()

        def add_path():
            path = filedialog.folder_dialog(".","select feature folder")
            if path == False:
                return
            if path not in self.serverconfig["feature_path_options"]:
                self.serverconfig["feature_path_options"].append(path)
                self.serverconfig["feature_path_options"] = self.serverconfig["feature_path_options"] # trigger save
                update_featurepaths_menu()
            else:
                print("path is already registered")

        def remove_path(path):
            if path in self.serverconfig["feature_path_options"]:
                self.serverconfig["feature_path_options"].remove(path)
                self.serverconfig["feature_path_options"] = self.serverconfig["feature_path_options"] # trigger save
                if path in self.serverconfig["feature_paths"]:
                    self.serverconfig["feature_paths"].remove(path)
                    self.serverconfig["feature_paths"] = self.serverconfig["feature_paths"] # trigger save
                    update_text()
                update_featurepaths_menu()
            else:
                print("warning: path couldn't be removed because it wasn't in there")

        def update_featurepaths_menu():
            featurepaths_menu.delete(0,"end")
            removal_menu = Tkinter.Menu(featurepaths_menu, tearoff=0)
            for path in self.serverconfig["feature_path_options"]:
                v = Tkinter.BooleanVar()
                v.set(path in self.serverconfig["feature_paths"])
                featurepaths_menu.add_checkbutton(label=path, onvalue=True, offvalue=False, variable=v, command=lambda p=path, v=v:update_selection(p, v))
                if path != "default":
                    removal_menu.add_command(label=path, command=lambda p=path:remove_path(p))
            featurepaths_menu.add_separator()
            featurepaths_menu.add_command(label="add path", command=add_path)
            featurepaths_menu.add_cascade(label="remove path",menu=removal_menu)
        update_featurepaths_menu()

        featurepaths_menubutton.grid(column = 1, columnspan=3, row = self.row, sticky = Tkinter.W+Tkinter.E)
        featurepaths_menubutton.configure(takefocus=1)
        self.row += 1
        
        self.disabled_when_running.append(featurepaths_menubutton)

    def set_running(self, value):
        self.queue["set_running"] = (self._set_running, (value,))

    def _set_running(self, value):
        if self.lock.acquire(False): # doing stuff when the window is already closed will block the application, so use lock to avoid destroying root while window get's used
            self.running = value
            self.startbutton.configure(text = "Stop" if self.running else "Start")
            self.playbutton.configure(text = "Play" if self.running else "Start & Play")
            for element in self.disabled_when_running:
                element.configure(state=("disabled" if self.running else "normal"))
            self.update_worldtypes()
            self.lock.release()

    def addwidgets_run_play(self):
        # Start/Stop
        def togglerun():
            self.root.focus()
            if not self.running:
                self.callback("run")
            else:
                self.callback("quit")
        self.startbutton = Tkinter.Button(self.root, command = togglerun)
        self.startbutton.grid(column = 1, row = self.row, sticky = Tkinter.W+Tkinter.E)

        # Play
        def play():
            self.root.focus()
            if not self.running:
                self.callback("run")
            self.callback("play")
        self.playbutton = Tkinter.Button(self.root, command = play)
        self.playbutton.grid(column = 2, columnspan = 2, row = self.row, sticky = Tkinter.W+Tkinter.E)
        
        self.row += 1
        self.set_running(False)
        self.playbutton.focus()

    def addwidgets_play(self):
        # Play
        def play():
            self.root.focus()
            self.callback("play")
        playbutton = Tkinter.Button(self.root, text = "Play", command = play)
        playbutton.grid(column = 1, columnspan = 3, row = self.row, sticky = Tkinter.W+Tkinter.E)
        self.row += 1
    
    def addwidgets_statsframe(self):
        self.statsframe = Tkinter.LabelFrame(self.root, text="Stats")
        self.statsframe.grid(column = 0, columnspan = 4, row = self.row, sticky = Tkinter.W+Tkinter.E)
        self.row += 1


    def addwidgets_serverlist(self):
        head = Tkinter.Label(self.root, text="Wähle einen Server zum Spielen")
        head.grid(row = self.row, column = 0, columnspan = 2)

        self.serverlistframe = VerticalScrolledFrame(self.root)
        self.serverlistframe.grid(row = self.row+1, column = 0, columnspan = 4, sticky = Tkinter.E+Tkinter.E)
    
        def refresh():
            self.root.focus()
            self.callback("refresh")
        refreshbutton = Tkinter.Button(self.root, text="Refresh", command = refresh)
        refreshbutton.grid(column = 2, columnspan = 2, row = self.row, sticky = Tkinter.W+Tkinter.E)

        self.row += 2

        # Address direct input
        def setaddress(address):
            self.clientconfig["address"] = address
        self.add_label("Address")
        self.addressentry = self.add_entry(self.clientconfig["address"], setaddress)
    
    def add_entry(self, content, callback):
        def apply_changes(event):
            callback(entry.get())
        def select_all(event):
            entry.select_range(0, 'end')
            #entry.icursor('end')
        entry = Tkinter.Entry(self.root)
        entry.insert(0, content)
        entry.grid(column = 1, row = self.row, sticky = Tkinter.W+Tkinter.E)
        entry.bind("<Return>",apply_changes)
        entry.bind("<FocusOut>",apply_changes)
        entry.bind('<Control-KeyRelease-a>', select_all)
        self.row += 1
        return entry
        
    def add_label(self, labeltext):
        label = Tkinter.Label(self.root, text=labeltext)
        label.grid(column = 0, row = self.row, sticky = Tkinter.W)
        return label

    def set_stats(self,name,value):
        self.queue[name] = (self._set_stats, (name,value))

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

    def show_servers(self, servers):
        self.queue["show_servers"] = (self._show_servers, (servers,))

    def _show_servers(self, servers):
        print(servers)
        for button in self.serverlistframe.interior.winfo_children():
            print(button)
            button.pack_forget()

        def add_button(text, command):
            btn = Tkinter.Button(self.serverlistframe.interior,
                height=1, width=50, relief=Tkinter.FLAT, 
                #bg="gray99", fg="purple3",
                #font="Dosis",
                text=text,
                anchor="w",
                command = command)
            btn.pack(padx=0, pady=0, side=Tkinter.TOP)
            
        for i,server in enumerate(servers):
            print(server)
            addr = "%s:%i" % (server["host"], server["http_port"])
            def func(addr = addr):
                self.addressentry.delete(0,Tkinter.END)
                self.addressentry.insert(0,addr)
                self.clientconfig["address"] = addr
            add_button(server["name"], func)
        if not servers:
            add_button("no server found", lambda:None)



class ServerGUI(GUI):
    def init_widgets(self):
        self.addwidgets_name()
        self.addwidgets_file()
        self.addwidgets_autosave()
        self.addwidgets_featurepaths()
        self.addwidgets_worldtype()
        self.addwidgets_mobspawning()
        self.addwidgets_gamemode()
        self.addwidgets_whitelist()
        self.addwidgets_server_parole()
        self.addwidgets_username_password()
        self.addwidgets_clienttype()
        self.addwidgets_run_play()
        self.addwidgets_statsframe()

class ClientGUI(GUI):
    def init_widgets(self):
        self.addwidgets_serverlist()
        self.addwidgets_client_parole()
        self.addwidgets_username_password()
        self.addwidgets_clienttype()
        self.addwidgets_play()

if __name__ == "__main__":
    serverconfig = {
                "name"     : "MCGCraft Server",
                "file"     : "",
                "worldtype": "Colorland",
                "mobspawning": False,
                "entitylimit" : 5,
                "gamemode" : "creative",
                "whitelist": ["127.0.0.1"],
                "parole"   : "",
                "feature_paths": ["essential","default"],
                "feature_path_options": ["essential","default", "weihnachtsdeko","/home/user/games/MCGCRAFT/custom"],
                "autosaveintervall": None,
    }
    clientconfig = {
                "username" : "",
                "password" : "",
                "clienttype": "desktop",
                "parole"   : "",
                "address"  : "",
    }
    def callback(cmd):
        if cmd == "run":
            gui.set_running(True)
        if cmd == "quit":
            gui.set_running(False)
    gui = ServerGUI(serverconfig, clientconfig, lambda:("one","two","three"), lambda:("desktop","web"), callback, background = True)
    #gui = ClientGUI(None, clientconfig, lambda:(), lambda:("desktop","web"))

    #import time
    #time.sleep(1)
    #gui.set_running(True)
    #gui.set_stats("fps","16")
    #gui.show_servers([])
    #gui.mainloop()
