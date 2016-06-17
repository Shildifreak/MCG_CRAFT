from voxelengine.multiplayer.server import *

class MC_PLAYER(Player):
    SPEED = 5
    RENDERDISTANCE = 16
    velocity = Vector([0,0,0])

    def handle_input(self,cmd):
        if cmd == "tick":
            self.sentcount = 0
        if cmd == "right click":
            v = hit_test(lambda v:self.world[v].get_id()!=0,self.position,
                         self.get_sight_vector())[1]
            if v:
                self.world[v].set_id("GRASS")
        if cmd == "left click":
            v = hit_test(lambda v:self.world[v].get_id()!=0,self.position,
                         self.get_sight_vector())[0]
            if v:
                self.world[v].set_id(0)
        if cmd.startswith("rot"):
            x,y = map(float,cmd.split(" ")[1:])
            self.rotation = x,y
        if cmd.startswith("keys"):
            action_states = int(cmd.split(" ")[1])
            for i,a in enumerate(ACTIONS):
                self.action_states[a] = bool(action_states & (1<<(i+1)))

    def onground(self):
        return True

    def update(self):
        ds = min(1,self.SPEED*(time.time()-self.last_update))
        self.last_update = time.time()
        if self.onground():
            sx,sy,sz = self.get_sight_vector()
            self.velocity = self.velocity*(0,1,0) #slowing down
            if self.sentcount <= MSGS_PER_TICK:
                if self.action_states["for"]:
                    self.velocity += ( sx,0, sz)
                if self.action_states["back"]:
                    self.velocity += (-sx,0,-sz)
                if self.action_states["right"]:
                    self.velocity += (-sz,0, sx)
                if self.action_states["left"]:
                    self.velocity += ( sz,0,-sx)
        self.set_position(self.position+self.velocity*ds)

if __name__ == "__main__":
    with Game([simple_terrain_generator],playerclass=MC_PLAYER) as g:
        while True:
            g.update()
            for player in g.get_players():
                player.update()
