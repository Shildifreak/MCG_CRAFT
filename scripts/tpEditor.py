#! /usr/bin/env python3
import os
import sys
import inspect

PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
os.chdir(os.path.join(PATH,"..","lib","TPManager"))
sys.path.append(".")

import manager
