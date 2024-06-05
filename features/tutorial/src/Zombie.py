from resources import *

@register_entity("Zombie")
class Zombie(Entity):
    LIMIT = 50

    def clicked(self, character, item):
        print("Au")
