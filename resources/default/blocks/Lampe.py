from resources import *

@register_block("LAMP")
class Lamp(SolidBlock):
    def handle_event_block_update(self,event):
        SolidBlock.handle_event_block_update(self,event)
        if self.redstone_activated():
            self["state"] = "ON"
        else:
            self["state"] = "OFF"
        self.save()

    def get_tags(self):
        return super().get_tags() | {"block_update"}
