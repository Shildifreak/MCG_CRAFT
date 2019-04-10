#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

if __name__ != "__main__":
    raise Warning("clientmitgui.py should not be imported")

# hack der nur bei uns in der Schule funktioniert, damit mcgcraft mit python2 ausgeführt wird
import os, sys
if sys.version >= "3":
    os.system("C:\\Python27\\python.exe clientmitgui.py") 
    sys.exit(0)

import sys, os
sys.path.append("lib")
import voxelengine.client as client
import Tkinter

def select(options):
    i = []
    window = Tkinter.Tk()
    head = Tkinter.Label(window, text="Wähle einen Server")
    head.grid(row = 0, column = 0)
    for nr,option in enumerate(options):
        o = Tkinter.Button(window, text=option)
        def func(nr=nr):
            i.append(nr)
            window.destroy()
        o.configure(command = func)
        o.grid(row = nr+1, column = 0, sticky=Tkinter.W+Tkinter.E)
    window.mainloop()
    return i[0],options[i[0]]

client.select = select
client.main()
