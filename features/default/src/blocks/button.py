from resources import *

class Button(Block):
    defaults = Block.defaults.copy()
    defaults["p_ambient"] = True
    defaults["p_level"] = 0
    
    def clicked(self,character,face,item):
        print("aha")
        face = FACES["tbsnwe".find(self["base"])]
        self["p_directions"] = (face,)

        self.press()
        self.save()

    def press(self):
        self["state"] = "Pressed"
        self["p_level"] = 15
        unpress_event = Event("unpress",Point(self.position))
        self.world.event_system.add_event(unpress_event, 60)

    def handle_event_unpress(self, events):
        if self["state"] == "Pressed":
            self["state"] = ""
            self["p_level"] = -15
            unpress_event = Event("unpress",Point(self.position))
            self.world.event_system.add_event(unpress_event, 60)
        else:
            self["p_level"] = 0
        return True
        
    def handle_event_entity_enter(self,events):
        for event in events:
            entity = event.data
            pass
        if self["state"] != "Pressed":
            self.press()
            return True
        return False

    def get_tags(self):
        return (super().get_tags() - {"solid"}) | {"entity_enter", "unpress"}

#   def collides_with(self,area):
#       return False
