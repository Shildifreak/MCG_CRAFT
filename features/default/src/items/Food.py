from resources import *

class Apple(UnplacableItem):
	def use_on_air(self, character):
		character["health"] += 1
	
	def use_on_entity(self, character, entity):
		entity["health"] += 1
