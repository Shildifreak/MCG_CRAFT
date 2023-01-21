import sys, os
if __name__ == "__main__":
	sys.path.append(os.path.abspath("../.."))
	__package__ = "voxelengine.server"

from collections import defaultdict
import threading
import warnings
import traceback
import pprint

from voxelengine.server.blocks.block_world import BlockWorld
from voxelengine.server.event_system import EventSystem, Event
from voxelengine.server.entities.entity_world import EntityWorld
from voxelengine.server.players.player_world import PlayerWorld

from voxelengine.modules.serializableCollections import Serializable, serialize, extended_literal_eval
from voxelengine.modules.geometry import Vector, Box, Sphere
from voxelengine.server.blocks.block import BlockFactory
from voxelengine.server.entities.entity import EntityFactory

warnings.filterwarnings("default", category=DeprecationWarning, module=__name__)
def warn_with_traceback(message, category, filename, lineno, file=None, line=None):
    log = file if hasattr(file,'write') else sys.stderr
    traceback.print_stack(file=log)
    log.write(warnings.formatwarning(message, category, filename, lineno, line))
warnings.showwarning = warn_with_traceback


class Clock(dict):
	def __init__(self, data):
		super().__init__(data)
		self.tick_event = threading.Event()
	current_gametick = property(lambda self:self["gametick"], lambda self, value:self.__setitem__("gametick",value))
	def tick(self):
		self.current_gametick += 1
		self.tick_event.set(); self.tick_event.clear()

class World(Serializable):
	def __init__(self, data, blockFactory=BlockFactory, entityFactory=EntityFactory):
		self.data = data
		self.clock        = data["metadata"]["clock"] = Clock(data["metadata"]["clock"])
		self.event_system = data["events"]            = EventSystem(self, data["events"])
		self.blocks       = data["block_world"]       = BlockWorld(self, data["block_world"], self.event_system, self.clock, blockFactory)
		self.entities     = data["entities"]          = EntityWorld(self, data["entities"], entityFactory)
		self.players                                  = PlayerWorld()
	
	def __serialize__(self):
		return self.data

	def __getitem__(self, *args, **kwargs):
		warnings.warn(DeprecationWarning("use world.blocks[...] instead of world[...]"))
		return self.blocks.__getitem__(*args,**kwargs)
	
	def __setitem__(self, *args, **kwargs):
		warnings.warn(DeprecationWarning("use world.blocks[...] instead of world[...]"))
		self.blocks.__setitem__(*args,**kwargs)

	def tick(self):
		# process pending events
		self.event_system.process_events()
		# tick
		self.event_system.tick()
		self.clock.tick()

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

if __name__ == "__main__":
	from voxelengine.server.world import World
	from voxelengine.server.world_data_template import data    
	data["block_world"]["generator"] = {
		"name":"Simple Terrain Generator",
		"seed":0,
		"path_py":"...",
		"code_py":"spawnpoint = (0,0,0)",
		"code_js":\
"""
function terrain(position) {
	// a very simple terrain generator -> flat map with checkerboard pattern
	if (position[1] == -2) {
		if ((position[0]+position[2])%2) {
			return "GREEN";
		} else {
			return "CYAN";
		}
	}
	return "AIR";
}
"""
	}

	w = World(data)

	assert w.blocks[(0,-2,0)] == "CYAN"
	w.blocks[(0,-2,0)] = "AIR"
	w.clock.current_gametick += 1
	assert w.blocks[(0,-2,0)] == "AIR"

	from voxelengine.server.entities.entity import Entity
	e = Entity()

