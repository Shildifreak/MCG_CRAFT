from resources import *
import random


class Apple(UnplacableItem):
	def use_on_air(self, character):
		character["health"] += 1
	
	def use_on_entity(self, character, entity):
		entity["health"] += 1

class Fish(UnplacableItem):
	def use_on_air(self, character):
		character["health"] += random.randint(-1,2)
	
	def use_on_entity(self, character, entity):
		entity["health"] += random.randint(-1,2)

