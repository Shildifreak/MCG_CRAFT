#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

if __name__ != "__main__":
    raise Warning("clientmitgui.py should not be imported")

import sys, os
sys.path.append("lib")
import voxelengine.client.client as client
import tkinter

def select(options):
    i = []
    window = tkinter.Tk()
    head = tkinter.Label(window, text="Wähle einen Server")
    head.grid(row = 0, column = 0)
    for nr,option in enumerate(options):
        o = tkinter.Button(window, text=option)
        def func(nr=nr):
            i.append(nr)
            window.destroy()
        o.configure(command = func)
        o.grid(row = nr+1, column = 0, sticky=tkinter.W+tkinter.E)
    window.mainloop()
    if i:
        return i[0],options[i[0]]
    else:
        sys.exit(0)

client.select = select
client.main()
