#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os
import runpy

if getattr(sys, 'frozen', False):
    import pyi_splash
    pyi_splash.close()

if len(sys.argv) > 1:
	path = sys.argv.pop(1)
else:
	path = "scripts/menu.py"

runpy.run_path(path,run_name="__main__")
