from resources import *

class ROCKET(Block):
    blast_resistance = 1
    delay = 10

    def handle_event_block_update(self,event):
        rocket_move_event = Event("rocket_move",Point(self.position))
        self.world.event_system.add_event(rocket_move_event, self.delay)
        return False
        
    def handle_event_rocket_move(self,event):
        v = self.get_front_facing_vector()
        if self.world.blocks[self.position+v] == "AIR":
            self.world.request_move_block(self.position, self.position+v, lambda worked: self.explode if not worked else None)
        else:
            self.explode()
            return True
        return False
    
    def explode(self):
        power = random.randint(3,7)
        explosion_event = Event("explosion",Sphere(self.position,power))
        self.world.event_system.add_event(explosion_event)
        self.turn_into("AIR")
    
    def get_tags(self):
        return super().get_tags() | {"block_update", "rocket_move"}
