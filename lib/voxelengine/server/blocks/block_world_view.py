

class BlockWorldView(object):
	__slots__ = ("blockworld", "origin")
	def __init__(self, blockworld, origin):
		self.blockworld = blockworld
		self.origin = origin
	
	def __getitem__(self, relative_position, t = 0, relative_timestep = True):
		return self.blockworld.__getitem__(self.origin + relative_position, t, relative_timestep)

	get = __getitem__

	def __setitem__(self, relative_position, value):
		self.blockworld[self.origin + relative_position] = value
