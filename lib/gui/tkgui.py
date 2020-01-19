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

class GUI(object):
    def __init__(self, config, worldtypes = (), clienttypes = (), background = True):
        self.queue = {}
        self.stats = {}
        self.lock = thread.allocate_lock() #lock that shows whether it is save to do window stuff
        self.config = config
        self.worldtypes = worldtypes
        self.clienttypes = clienttypes
        
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
        try:
            while 1:
                time.sleep(0.01)
                self.update()
        except:
            pass

    def update(self):
        self.root.update()
        while self.queue:
            id, (func, args) = self.queue.popitem()
            func(*args)

    def quit(self):
        self.config["quit"] = True
        try:
            self.root.destroy()
        except:
            pass

    def create_window(self):
        # WINDOW
        root = Tkinter.Tk()
        root.title("MCGCraft Server GUI")
        def on_closing():
            self.config["run"] = False
            self.config["quit"] = True
            self.lock.acquire() #wait for lock to be available, lock forever because no one will be able to use window once it's destroyed
            root.destroy()
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.protocol("WM_SAVE_YOURSELF", on_closing)
        root.grid_columnconfigure(1,weight=1)
        self.root = root
        self.row = 0
        
    def addwidgets_name(self):
        # Name des Spiels
        def setname(name):
            self.config["name"] = name
        self.add_label("Name")
        self.add_entry(self.config["name"], setname)

    def addwidgets_file(self):
        # Speicherort
        def setfile(fn, autocorrect=False):
            if fn == self.config["file"]:
                return
            if not fn.endswith(".mc.zip") and autocorrect:
                fn += ".mc.zip"
            fileentry.delete(0, Tkinter.END)
            fileentry.insert(0,fn)
            fileentry.xview_moveto(1)
            self.config["file"] = fn
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
        fileentry = self.add_entry(self.config["file"], file_focus_out)
        defaultfg = fileentry["fg"]
        fileentry.xview_moveto(1)
        fileentry.bind("<FocusIn>",file_focus_in)
        file_focus_out(None)
        
        def openfile():
            fn = filedialog.open_dialog("")
            if fn != False:
                setfile(fn, False)
        fileopenbutton = Tkinter.Button(self.root, text="öffnen", command=openfile)
        fileopenbutton.grid(column = 2, row = self.row-1, sticky = Tkinter.W+Tkinter.E)
        def newfile():
            fn = filedialog.save_dialog("")
            if fn != False:
                setfile(fn, True)
        filenewbutton = Tkinter.Button(self.root, text="neu", command=newfile)
        filenewbutton.grid(column = 3, row = self.row-1, sticky = Tkinter.W+Tkinter.E)

    def addwidgets_worldtype(self):
        # Worldtype #http://effbot.org/tkinterbook/optionmenu.htm
        def setworldtype(*args):
            self.config["worldtype"] = wtvar.get()
        wtvar = Tkinter.StringVar(self.root)
        wtvar.set(self.config["worldtype"]) # default value
        wtvar.trace("w",setworldtype)
        if self.config["worldtype"] not in self.worldtypes:
            self.worldtypes = (self.config["worldtype"],) + tuple(self.worldtypes)

        self.add_label("Welttyp")
        wtmenu = Tkinter.OptionMenu(self.root, wtvar, *self.worldtypes)
        wtmenu.grid(column = 1, row = self.row, sticky = Tkinter.W+Tkinter.E)
        wtmenu.configure(takefocus=1)
        self.row += 1

    def addwidgets_mobspawning(self):
        # Mob Spawning
        def setmobspawning(*args):
            self.config["mobspawning"] = bool(mobspawningvar.get())
        mobspawningvar = Tkinter.IntVar(self.root)
        mobspawningvar.set(self.config["mobspawning"])
        mobspawningvar.trace("w",setmobspawning)
        self.add_label("Mob Spawning")
        mobspawning_checkbutton = Tkinter.Checkbutton(self.root, variable = mobspawningvar)
        mobspawning_checkbutton.grid(column = 1, row = self.row, sticky = Tkinter.W)
        self.row += 1
        
    def addwidgets_whitelist(self):
        # Whitelist
        def setwhitelist(*args):
            self.config["whitelist"] = whitelistvar.get()
        whitelistvar = Tkinter.StringVar(self.root)
        whitelistvar.set(self.config["whitelist"])
        whitelistvar.trace("w",setwhitelist)
        self.add_label("Whitelist")
        whitelist_entry = Tkinter.Entry(self.root, textvariable = whitelistvar)
        whitelist_entry.grid(column = 1, row = self.row, sticky = Tkinter.W+Tkinter.E)
        whitelist_button_local = Tkinter.Radiobutton(text = "localhost", variable = whitelistvar, value = "127.0.0.1")
        whitelist_button_local.grid(column = 2, row = self.row, sticky = Tkinter.W)
        whitelist_button_LAN = Tkinter.Radiobutton(text = "LAN", variable = whitelistvar, value = "192.168.0.0/16")
        whitelist_button_LAN.grid(column = 3, row = self.row, sticky = Tkinter.W)
        self.row += 3

    def addwidgets_parole(self):
        # Parole
        def setparole(parole):
            self.config["parole"] = parole
        self.add_label("Parole")
        self.add_entry(self.config["parole"], setparole)

    def addwidgets_username_password(self):
        # Username
        def setusername(username):
            self.config["username"] = username
            if username:
                self.passwordlabel.grid()
                self.passwordentry.grid()
            else:
                self.passwordlabel.grid_remove()
                self.passwordentry.grid_remove()
                
        self.add_label("Username")
        self.add_entry(self.config["username"], setusername)

        # Password
        def setpassword(password):
            self.config["password"] = password
        self.passwordlabel = self.add_label("Password")
        self.passwordentry = self.add_entry(self.config["password"], setpassword)

        setusername(self.config["username"])

    def addwidgets_clienttype(self):
        # Client type
        def setclienttype(*args):
            self.config["clienttype"] = clienttypevar.get()        
        clienttypevar = Tkinter.StringVar(self.root)
        clienttypevar.set(self.config["clienttype"])
        clienttypevar.trace("w",setclienttype)
        
        clienttype_button_desktop = Tkinter.Radiobutton(text = "Desktop", variable = clienttypevar, value = "desktop")
        clienttype_button_desktop.grid(column = 2, row = self.row, sticky = Tkinter.W)
        clienttype_button_web = Tkinter.Radiobutton(text = "Web", variable = clienttypevar, value = "web")
        clienttype_button_web.grid(column = 3, row = self.row, sticky = Tkinter.W)

        if self.config["clienttype"] not in self.clienttypes:
            self.clienttypes = (self.config["clienttype"],) + tuple(self.clienttypes)

        self.add_label("Client Type")
        clienttype_menu = Tkinter.OptionMenu(self.root, clienttypevar, *self.clienttypes)
        clienttype_menu.grid(column = 1, row = self.row, sticky = Tkinter.W+Tkinter.E)
        clienttype_menu.configure(takefocus=1)
        self.row += 1
        

    def addwidgets_texturepack(self):
        # Texturepack
        texturepacktypes = ("default_stable", "weihnachtsdeko", "default")

        def settexturepack(*args):
            self.config["texturepack"] = texturepackvar.get()        
        texturepackvar = Tkinter.StringVar(self.root)
        texturepackvar.set(self.config["texturepack"])
        texturepackvar.trace("w",settexturepack)
        
        if self.config["texturepack"] not in texturepacktypes:
            texturepacktypes = (self.config["texturepack"],) + tuple(texturepacktypes)

        self.add_label("Texturepack")
        texturepack_menu = Tkinter.OptionMenu(self.root, texturepackvar, *texturepacktypes)
        texturepack_menu.grid(column = 1, row = self.row, sticky = Tkinter.W+Tkinter.E)
        texturepack_menu.configure(takefocus=1)
        self.row += 1

    def addwidgets_run_play(self):
        # Start/Stop
        def togglerun():
            self.root.focus()
            self.config["run"] = not self.config["run"]
            update_buttontexts()
        startbutton = Tkinter.Button(self.root, command = togglerun)
        startbutton.grid(column = 1, row = self.row, sticky = Tkinter.W+Tkinter.E)

        # Play
        def play():
            self.root.focus()
            self.config["run"] = True
            self.config["play"] = True
            update_buttontexts()
        playbutton = Tkinter.Button(self.root, command = play)
        playbutton.grid(column = 2, columnspan = 2, row = self.row, sticky = Tkinter.W+Tkinter.E)
        
        # SAVE?
        
        # BUTTONS
        def update_buttontexts():
            startbutton.configure(text = "Stop" if self.config["run"] else "Start")
            playbutton.configure(text = "Play" if self.config["run"] else "Start & Play")
        update_buttontexts()
        self.row += 1

        playbutton.focus()
    
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
            self.config["refresh"] = True
        refreshbutton = Tkinter.Button(self.root, text="Refresh", command = refresh)
        refreshbutton.grid(column = 2, columnspan = 2, row = self.row, sticky = Tkinter.W+Tkinter.E)

        self.row += 2
    
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
            addr, name = server
            def func(addr = addr):
                self.config["address"] = addr
            add_button(name, func)
        if not servers:
            add_button("no server found", lambda:None)



class ServerGUI(GUI):
    def init_widgets(self):
        self.addwidgets_name()
        self.addwidgets_file()
        self.addwidgets_worldtype()
        self.addwidgets_mobspawning()
        self.addwidgets_whitelist()
        self.addwidgets_parole()
        self.addwidgets_username_password()
        self.addwidgets_clienttype()
        self.addwidgets_texturepack()
        self.addwidgets_run_play()
        self.addwidgets_statsframe()

class ClientGUI(GUI):
    def init_widgets(self):
        self.addwidgets_serverlist()
        self.addwidgets_parole()
        self.addwidgets_username_password()
        self.addwidgets_clienttype()

if __name__ == "__main__":
    config = {  "name"     : "MCGCraft Server",
                "file"     : "",
                "worldtype": "Colorland",
                "mobspawning": False,
                "whitelist": "127.0.0.1",
                "parole"   : "",
                "username" : "",
                "password" : "",
                "clienttype": "desktop",
                "texturepack": "default",
                "port"     : "",
                "address"  : None,
                "run"      : False,
                "play"     : False,
                "quit"     : False,
                "save"     : False,
                "refresh"  : False}
    #gui = ServerGUI(config, ("one","two","three"), ("desktop","web"), background = True)
    gui = ClientGUI(config)

    import time
    time.sleep(1)
    #gui.set_stats("fps","16")
    gui.show_servers([])

        
