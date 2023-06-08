python3 -m PyInstaller -F \
--hidden-import json \
--hidden-import tkinter \
--hidden-import tkinter.filedialog \
--hidden-import ctypes \
--hidden-import ctypes.util \
--hidden-import ipaddress \
--hidden-import pkg_resources \
--hidden-import queue \
--hidden-import pygame \
--hidden-import gi \
--hidden-import gi.repository \
--hidden-import wave \
launcher.py
# -p lib/voxelengine/modules \
# --hidden-import pyglet \
# --hidden-import py_mini_racer \
# --add-binary lib/voxelengine/modules/py_mini_racer/_v8.win32.so:_v8 \
