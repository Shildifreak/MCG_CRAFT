#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import sys, os

root = tk.Tk()

selected_script = None
def callback(script):
	def select_script():
		global selected_script
		root.destroy()
		selected_script = script
	return select_script

tk.Button(root, command=callback("startGame"),    text="Start Game"   ).pack(fill=tk.X)
tk.Button(root, command=callback("joinGame"),     text="Join Game"    ).pack(fill=tk.X)
tk.Button(root, command=callback("editControls"), text="Edit Controls").pack(fill=tk.X)

root.mainloop()

if selected_script:
	sys.path.append("scripts")
	__import__(selected_script)
