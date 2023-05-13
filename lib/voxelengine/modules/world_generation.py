import types
import random
import warnings
import functools

import sys, os, inspect
PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(PATH)
from voxelengine.modules.py_mini_racer import py_mini_racer

from voxelengine.modules.frozen_dict import freeze


class WorldGenerator(object):
	def __init__(self, generator_data, init_py=True, init_js=True):
		self.generator_data = generator_data
		if init_py:
			self._init_py()
		if init_js:
			self._init_js()

	def _init_py(self):
		# creating the module
		generator_module = self.generator_module = types.ModuleType(self.generator_data["name"])

		# setting stuff up
		generator_module.seed = self.generator_data["seed"]
		random.seed(generator_module.seed)

		# running module code
		code = compile(self.generator_data["code_py"], self.generator_data["path_py"], "exec")
		exec(code, generator_module.__dict__)

		# cleaning stuff up
		random.seed()
		if hasattr(generator_module, "terrain") or hasattr(generator_module, "terrain_js"):
			raise DeprecationWarning("terrain functions in python file are ignored, consider creating a .js file")
		if not hasattr(generator_module, "init"):
			generator_module.init = empty_init

	def _init_js(self):
		if self.generator_data["code_js"]:
			self.js_context = py_mini_racer.MiniRacer()
			self.js_context.eval("var seed = %s;" % self.generator_data["seed"])
			self.js_context.eval(self.generator_data["code_js"])
			self.js_context.eval(default_functions_js)
		else:
			# overwrite methods for performance improvement of not calling js_context all the time
			self.terrain = empty_terrain
			self.client_terrain = empty_terrain
			self.terrain_hint = empty_terrain_hint
			self.sky = empty_sky

	def init(self, world):
		random.seed(self.generator_data["seed"])
		self.generator_module.init(world)
		random.seed()

	@property
	def spawnpoint(self):
		if hasattr(self.generator_module, "spawnpoint"):
			return self.generator_module.spawnpoint
		elif hasattr(self, "js_context") and self.js_context.eval('typeof spawnpoint !== "undefined"'):
			return self.js_context.eval("spawnpoint")
		else:
			return (0,0,0)

	@functools.lru_cache(10000)
	def client_terrain(self, position):
		block = self._terrain(position)
		if isinstance(block, str):
			return block
		else:
			orientation = block.get("base","")+str(block.get("rotation",""))
			blockmodel = block["id"]+block.get("state","")
			if orientation:
				return blockmodel+":"+orientation
			else:
				return blockmodel

	@functools.lru_cache(10000)
	def terrain(self, position):
		return freeze(self._terrain(position))

	def _terrain(self, position):
		"""uncached version of terrain, replaced by array lookup during preload phase"""
		blockdata = self.js_context.call("terrain", position)
		return blockdata
		
	def terrain_hint(self, binary_box, tag):
		return self.js_context.call("terrain_hint", binary_box, tag)

	def sky(self, position, time):
		return self.js_context.call("sky", position, time)

	def preload(self, positions):
		values = self.js_context.call("((positions)=>positions.map(terrain))", positions)
		
		# get stuff into cache
		original_terrain_func = self._terrain
		self._terrain = lambda position: value
		for position, value in zip(positions, values):
			self.client_terrain(position)
		self._terrain = original_terrain_func

#terrain_mapped_js = """
#function terrain_mapped(positions) {
#	return positions.map(terrain);
#}
#"""


default_functions_js = """

if (typeof terrain === "undefined") {
	function terrain(position) {
		return "AIR";
	}
	function terrain_hint(binary_box,tag) {
		switch(String(tag)) {
			case "visible":
				return false
			default:
				return true;
		}
	}
}

if (typeof terrain_hint === "undefined") {
	function terrain_hint(binary_box,tag) {
		return true;
	}
}

if (typeof sky === "undefined") {
	function sky(position, time) {
		return [0.5, 0.69, 1.0, 1];
	}
}

"""

def empty_init(world):
	pass

def empty_terrain(position):
	return "AIR"

def empty_terrain_hint(binary_box, tag):
	if tag == "visible":
		return False
	return True

def empty_sky(position, time):
	return (0.5, 0.69, 1.0, 1)
