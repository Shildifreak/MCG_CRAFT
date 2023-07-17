from resources import *

@register_block("SCHILDBLOCK")
class Sign(Block):
    defaults = Block.defaults.copy()
    defaults["text"] = "Schreibe eine Nachricht, während du neben dem Schild stehst."

    def clicked(self, character, face, item):
        area = Point(self.position)
        event = Event("chat", area, self["text"])
        self.world.event_system.add_event(event)

    def handle_event_chat(self, events):
        for event in events:
            msg = event.data
            if msg.startswith("[Schild]"):
                continue
            if not msg.startswith("["):
                continue
            self["text"] = "[Schild]" + msg

            area = Point(self.position)
            event = Event("chat", area, "Schildblock hat sich deine Nachricht gemerkt.")
            self.world.event_system.add_event(event)
            return True
        return False

    def get_tags(self):
        return super().get_tags() | {"chat"}
