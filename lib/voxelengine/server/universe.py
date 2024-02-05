import sys, os
if __name__ == "__main__":
	sys.path.append(os.path.abspath("../.."))
	__package__ = "voxelengine.server"

import voxelengine.server.world_data_template
from voxelengine.server.world import World
from voxelengine.modules.serializableCollections import Serializable, serialize, extended_literal_eval
from voxelengine.modules.geometry import Vector, Box, Sphere
from voxelengine.server.event_system import Event

class Universe(Serializable):
	def __init__(self, data=(), WorldFactory=World):
		self.WorldFactory = WorldFactory
		self.worlds = []
		for world_data in data:
			self.new_world(world_data)

	def __serialize__(self):
		return self.worlds

	def get_spawn_world(self):
		return self.worlds[0]

	def get_loaded_worlds(self):
		return [w for w in self.worlds if w.players]

	def new_world(self, data = voxelengine.server.world_data_template.data):
		world = self.WorldFactory(self, data)
		self.worlds.append(world)
		return world

	def tick(self, dt):
		for world in self.get_loaded_worlds():
			world.tick(dt)

	@staticmethod
	def parse_data_from_string(string):
		save_constructors = {"Vector":Vector,
		                     "Box"   :Box,
		                     "Sphere":Sphere,
		                     "Event" :Event,
		                     }
		return extended_literal_eval(string, save_constructors)
	
	def serialize(self):
		return serialize(self, (Vector, Box, Sphere, Event))

