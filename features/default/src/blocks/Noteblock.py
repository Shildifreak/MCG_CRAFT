from resources import *


class Noteblock(Block):

    def get_tags(self):
        return super().get_tags() | {"block_update"}

    def handle_event_block_update(self,event):
        if self.redstone_activated() and self.get("last_played",0) + 20 < self.world.clock.current_gametick:
            self["last_played"]=self.world.clock.current_gametick

            sound = self.relative[(0,-1,0)].get_break_sound()
            sound_event = Event("sound",Point(self.position),sound)
            self.world.event_system.add_event(sound_event)
            return True
        return False
