from resources import *


class Noteblock(Block):

    def get_tags(self):
        return super().get_tags() | {"block_update","delayed_update"}

    def handle_event_block_update(self,_):
        self.world.event_system.add_event(Event("delayed_update",Point(self.position),None))
        return False
        
    def handle_event_delayed_update(self,_):
        if self.redstone_activated(-1) and self.get("last_played",0) + 5 < self.world.clock.current_gametick:
            self["last_played"]=self.world.clock.current_gametick

#            sounds = self.relative[(0,1,0):-1].get_break_sounds()
            source = self.world.blocks.get(self.position+(0,1,0), t=-1)
            sounds = source.get_break_sounds()
            for sound in sounds:
                print(sound)
                sound_event = Event("sound",Point(self.position),sound)
                self.world.event_system.add_event(sound_event)
            return True
        return False
