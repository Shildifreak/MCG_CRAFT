import sys,os,inspect
import importlib

from base import *

if __name__ == "__main__":
    print "can (for some reason I do not fully understand) only be executed as package"

# Finding real current path
PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
files = os.listdir(PATH)
modules = [x[:-3] for x in files if x.endswith(".py") and not x.startswith("_")]
print "using resources", modules
for module in modules:
    if module != "__init__":
        importlib.import_module("."+module,__name__)
