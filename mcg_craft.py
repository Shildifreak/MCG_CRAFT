from voxelengine.multiplayer.server import *

class MC_PLAYER(Player):
    SPEED = 5
    RENDERDISTANCE = 16
    JUMPSPEED = 3
    GRAVITY = 1
    velocity = Vector([0,0,0])
    SLIDING = 0

    def handle_input(self,cmd):
        if cmd == "tick":
            self.sentcount = 0
        if cmd == "right click":
            v = hit_test(lambda v:self.world[v].get_id()!=0,self.position,
                         self.get_sight_vector())[1]
            if v:
                self.world[v].set_id("GRASS")
                if v in self.collide(self.position):
                    self.world[v].set_id(0)
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
        #M# integrate playersize
        return self.world[(self.position+(0,-2,0)).normalize()].get_id() not in ("AIR",0)

    def collide(self,position):
        #M# integrate hitbox
        head = (0,0,0)
        feet = (0,-1.8,0)
        blocks = set()
        for relpos in (head,feet):
            block_pos = (position+relpos).normalize()
            if self.world[block_pos].get_id() not in ("AIR",0):
                blocks.add(block_pos)
        return blocks

    def collide_difference(self,new_position,previous_position):
        """return blocks player collides with excluding the ones he already collides with"""
        return self.collide(new_position).difference(self.collide(previous_position))

    def update(self):
        if self.sentcount <= MSGS_PER_TICK: # freeze player if client doesnt respond
            dt = time.time()-self.last_update
            # slow time down for player if server is pretty slow
            dt = min(dt,1)
            self.last_update = time.time()
            if self.onground():
                sx,sy,sz = self.get_sight_vector()*self.SPEED
                self.velocity *= (self.SLIDING,0,self.SLIDING) #M# make slide depend on Block?
                if self.action_states["for"]:
                    self.velocity += ( sx,0, sz)
                if self.action_states["back"]:
                    self.velocity += (-sx,0,-sz)
                if self.action_states["right"]:
                    self.velocity += (-sz,0, sx)
                if self.action_states["left"]:
                    self.velocity += ( sz,0,-sx)
                if self.action_states["jump"]:
                    self.velocity += (0,self.JUMPSPEED,0)
            else:
                self.velocity -= Vector([0,1,0])*self.GRAVITY*dt
            steps = int(math.ceil(max(map(abs,self.velocity*dt))))*10
            pos = self.position
            for step in range(steps):
                for i in range(DIMENSION):
                    mask          = tuple([int(i==j) for j in range(DIMENSION)])
                    inverted_mask = tuple([int(i!=j) for j in range(DIMENSION)])
                    new = pos + self.velocity*dt*mask*(1.0/steps)
                    if self.collide_difference(new,pos):
                        self.velocity *= inverted_mask
                    else:
                        pos = new
            self.set_position(pos)

if __name__ == "__main__":
    with Game([simple_terrain_generator],playerclass=MC_PLAYER) as g:
        while True:
            g.update()
            for player in g.get_players():
                player.update()