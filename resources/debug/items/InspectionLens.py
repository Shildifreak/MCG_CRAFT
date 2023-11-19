from resources import *

import pprint

@register_item("Inspection_Lens")
class InspectionLens(Item):
    def _show(self, output, character):
        print(output)
        area = Point(character["position"])
        event = Event("chat", area, output)
        character.world.event_system.add_event(event)

    def use_on_block(self, character, block, face):
        self._show(pprint.pformat(block), character)

    def use_on_entity(self, character, entity):
        suppressed = ("password", "inventory")
        filtered_entity = {k:(v if k not in suppressed else "...") for k,v in entity.items()}
        self._show(pprint.pformat(filtered_entity), character)
    
    def use_on_air(self, character):
        self.use_on_entity(character, character)
