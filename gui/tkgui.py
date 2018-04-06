#* encoding:utf-8 *#

import sys
if sys.version < "3":
    import Tkinter
    import thread
else:
    import tkinter as Tkinter
    import _thread as thread
import filedialog

class GUI(object):
    def __init__(self, config, worldtypes = (), background = True):
        if background:
            thread.start_new_thread(self.init,(config,worldtypes))
        else:
            self.init(config,worldtypes)

    def init(self, config, worldtypes):
        # WINDOW
        root = Tkinter.Tk()
        root.title("MCGCraft Server GUI")
        def on_closing():
            config["run"] = False
            config["quit"] = True
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
            if fn and not fn.endswith(".mc.zip") and autocorrect:
                fn += ".mc.zip"
            fileentry.delete(0, Tkinter.END)
            fileentry.insert(0,fn)
            fileentry.xview_moveto(1)
            config["file"] = fn
        self.add_label("Speicherort")
        fileentry = self.add_entry(config["file"], setfile)
        
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
        self.row += 1
        
        # Whitelist
        def setwhitelist(*args):
            config["whitelist"] = whitelistvar.get()
        whitelistvar = Tkinter.StringVar(root)
        whitelistvar.set(config["whitelist"])
        whitelistvar.trace("w",setwhitelist)
        self.add_label("Whitelist")
        whitelist_button_local = Tkinter.Radiobutton(text = "localhost", variable = whitelistvar, value = "127.0.0.1")
        whitelist_button_local.grid(column = 2, row = self.row, sticky = Tkinter.W)
        whitelist_button_local = Tkinter.Radiobutton(text = "LAN", variable = whitelistvar, value = "192.168.0.0/16")
        whitelist_button_local.grid(column = 3, row = self.row, sticky = Tkinter.W)
        whitelist_entry = Tkinter.Entry(root, textvariable = whitelistvar)
        whitelist_entry.grid(column = 1, row = self.row, sticky = Tkinter.W+Tkinter.E)
        self.row += 3
        
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
        
        # BUTTONS
        def update_buttontexts():
            startbutton.configure(text = "Stop" if config["run"] else "Start")
            playbutton.configure(text = "Play" if config["run"] else "Start & Play")
        update_buttontexts()
        
        root.mainloop()

    def stats(self,name,value):
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

if __name__ == "__main__":
    config = {  "name"     : "MCGCraft Server",
                "file"     : "",
                "worldtype": "Colorland",
                "whitelist": "localhost",
                "parole"   : "",
                "port"     : "",
                "run"      : False,
                "play"     : False,
                "quit"     : False}
    gui = GUI(config, ("one","two","three"), background = False)
