class PlayerWorld(object):
	"""For now this class is pretty trivial, but one day it will help implement dynamic loading of the world"""

	def __init__(self, player_data):
		if player_data:
			raise NotImplementedError()
		self.players = set()

	def find_players(self, area, tag):
		"""players may be different in size in regards to different tags"""
		
		for player in self.players:
			if player.monitored_area.collides_with(area):
				yield player
		#if tag.startswith("entity"):
		#	return self.players
		#else:
		#	return None

	def add(self, player):
		self.players.add(player)

	def remove(self, player):
		self.players.remove(player)
