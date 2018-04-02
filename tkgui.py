import Tkinter
import thread

class GUI(object):
    def __init__(self, config, background = True):
        if background:
            thread.start_new_thread(self.init,(config,))
        else:
            self.init(config)

    def init(self, config):
        # WINDOW
        root = Tkinter.Tk()
        root.title("MCGCraft Server GUI")
        def on_closing():
            config["run"] = False
            root.destroy()
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.protocol("WM_SAVE_YOURSELF", on_closing)

        # Name des Spiels
        namelabel = Tkinter.Label(root, text="Name")
        namelabel.grid(column = 0, row = 0)
        nameentry = Tkinter.Entry(root)
        nameentry.insert(0, config["name"]) 
        nameentry.grid(column = 1, row = 0)

        # START/STOP
        startbutton = Tkinter.Button(root)
        def togglerun():
            config["run"] = not config["run"]
            startbutton.configure(text = "Stop" if config["run"] else "Start")
        startbutton.configure(text = "Stop" if config["run"] else "Start")
        startbutton.configure(command = togglerun)
        startbutton.grid(column = 0, row = 5)
        
        self.root = root
        root.mainloop()

    def stats(self,name,value):
        pass

if __name__ == "__main__":
    config = {  "name"     : "MCGCraft Server",
                "file"     : "",
                "worldtype": "Colorland",
                "whitelist": "localhost",
                "parole"   : "",
                "run"    : False}
    gui = GUI(config)
