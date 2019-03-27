from resources import *

@register_block("TORCH")
class Torch(Block):
	defaults = Block.defaults.copy()
	defaults["p_directions"] = (Vector((0,1,0)),)
	def block_update(self,directions):
		# check block torch is attached to for redstone signal
		basevector = self.get_base_vector()
		block = self.world[self.position + basevector]
		if block["p_level"]:
			self["p_level"] = 0
			self["p_stronglevel"] = 0
			self["state"] = "OFF"
		else:
			self["p_level"] = 15
			self["p_stronglevel"] = 15
			self["state"] = "ON"
	def collides_with(self,hitbox,position):
		return False

