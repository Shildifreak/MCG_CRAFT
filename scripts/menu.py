#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import os
import runpy

root = tk.Tk()

selected_script = None
def callback(script):
	def select_script():
		global selected_script
		root.destroy()
		selected_script = script
	return select_script

b = tk.Button(root, command=callback("startGame"),           text="Start Game"       ); b.pack(fill=tk.X); b.focus_set()
tk.Button(    root, command=callback("joinGame"),            text="Join Game"           ).pack(fill=tk.X)
tk.Button(    root, command=callback("editControls2"),       text="Edit Controls"       ).pack(fill=tk.X)
tk.Button(    root, command=callback("tpEditor"),            text="Edit Textures"       ).pack(fill=tk.X)
tk.Button(    root, command=callback("update"),              text="Update"              ).pack(fill=tk.X)

root.mainloop()

if selected_script:
	path = os.path.join("scripts",selected_script+".py")
	runpy.run_path(path)
