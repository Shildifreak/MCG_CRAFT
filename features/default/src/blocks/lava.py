from resources import *


class LAVA(Block):
    def get_tags(self):
        return (super().get_tags() - {"solid"}) | {"water"} | {"entity_enter"}

    def collides_with(self, area):
        return False

    def handle_event_entity_enter(self,events):
        for event in events:
            entity = event.data
            entity.take_damage(1)
        return False
