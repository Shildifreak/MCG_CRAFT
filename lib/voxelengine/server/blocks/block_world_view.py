

class BlockWorldView(object):
	__slots__ = ("blockworld", "origin")
	def __init__(self, blockworld, origin):
		self.blockworld = blockworld
		self.origin = origin
	
	def __getitem__(self, relative_position):
		return self.blockworld[self.origin + relative_position]

	def __setitem__(self, relative_position, value):
		self.blockworld[self.origin + relative_position] = value
