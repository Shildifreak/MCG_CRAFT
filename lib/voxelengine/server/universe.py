import sys, os
if __name__ == "__main__":
	sys.path.append(os.path.abspath("../.."))
	__package__ = "voxelengine.server"

import voxelengine.server.world_data_template
from voxelengine.server.world import World

class Universe(object):
	def __init__(self):
		self.worlds = []

	def get_spawn_world(self):
		return self.worlds[0]

	def new_world(self,	data = voxelengine.server.world_data_template.data):
		world = World(data)
		self.worlds.append(world)
		return world
