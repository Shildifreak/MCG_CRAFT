#import pygame as pygame1
#import sys
#import pprint
#for key in tuple(sys.modules.keys()):
#	if key.startswith("pygame"):
#		del sys.modules[key]
#import pygame as pygame2

import importlib
spec = importlib.util.find_spec("pygame")
pygame1 = importlib.util.module_from_spec(spec)
pygame2 = importlib.util.module_from_spec(spec)

display_spec = importlib.util.find_spec("pygame.display")
pygame1.display = importlib.util.module_from_spec(display_spec)
pygame2.display = importlib.util.module_from_spec(display_spec)

pygame1.display.set_mode((100,200))
pygame2.display.set_mode((200,100))
