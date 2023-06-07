python -m PyInstaller -F -p lib -p lib/voxelengine/modules -p scripts --add-binary lib/voxelengine/modules/py_mini_racer/_v8.win32.so;_v8 --hidden-import json --hidden-import tkinter.filedialog --hidden-import ctypes --hidden-import ipaddress --hidden-import mcgcraft --hidden-import pkg_resources --hidden-import voxelengine.modules.pyglet --hidden-import editControls --hidden-import editControls2 --hidden-import joinGame --hidden-import startGame --hidden-import tpEditor --hidden-import update launcher.py

python -m PyInstaller -F -p lib -p lib/voxelengine/modules --add-binary lib/voxelengine/modules/py_mini_racer/_v8.win32.so;_v8 --hidden-import ctypes --hidden-import ipaddress --hidden-import pkg_resources mcgcraft.py

