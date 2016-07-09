from voxelengine.multiplayer.server import *

class MC_PLAYER(Player):
    SPEED = 5
    AIRRESISTANCE = 0.9
    RENDERDISTANCE = 16
    JUMPSPEED = 10
    GRAVITY = 30
    SLIDING = 0.001
    HEIGHT = 1.8
    EYE_LEVEL = 1.6
    WIDTH = 0.4

    HITBOX = [(dx,dy,dz) for dx in (WIDTH,-WIDTH) for dy in (HEIGHT-EYE_LEVEL,-EYE_LEVEL) for dz in (WIDTH,-WIDTH)]
    
    velocity = Vector([0,0,0])
    flying = False

    def handle_input(self,cmd):
        if cmd == "tick":
            self.sentcount = 0
        if cmd == "right click":
            v = hit_test(lambda v:self.world[v]!=0,self.position,
                         self.get_sight_vector())[1]
            if v:
                self.world[v] = BLOCK_ID_BY_NAME["GRASS"]
                if v in self.collide(self.position):
                    self.world[v] = BLOCK_ID_BY_NAME["AIR"]
        if cmd == "left click":
            v = hit_test(lambda v:self.world[v]!=0,self.position,
                         self.get_sight_vector())[0]
            if v:
                self.world[v] = BLOCK_ID_BY_NAME["AIR"]
        if cmd.startswith("rot"):
            x,y = map(float,cmd.split(" ")[1:])
            self.rotation = x,y
        if cmd.startswith("keys"):
            action_states = int(cmd.split(" ")[1])
            for i,a in enumerate(ACTIONS):
                self.action_states[a] = bool(action_states & (1<<(i+1)))

    def onground(self):
        for relpos in self.HITBOX:
            block_pos = (self.position+relpos+(0,-0.2,0)).normalize()
            if self.world[block_pos] != BLOCK_ID_BY_NAME["AIR"]:
                return True
        return False

    def collide(self,position):
        blocks = set()
        for relpos in self.HITBOX:
            block_pos = (position+relpos).normalize()
            if self.world[block_pos] != BLOCK_ID_BY_NAME["AIR"]:
                blocks.add(block_pos)
        return blocks

    def collide_difference(self,new_position,previous_position):
        """return blocks player collides with excluding the ones he already collides with"""
        return self.collide(new_position).difference(self.collide(previous_position))

    def update(self):
        if self.flying:
            if self.action_states["for"]:
                print self.position
                self.set_position(self.position+self.get_sight_vector()*0.2)
            return
        #M# make sliding depend on block?
        if self.sentcount <= MSGS_PER_TICK: # freeze player if client doesnt respond
            dt = time.time()-self.last_update
            # slow time down for player if server is pretty slow
            dt = min(dt,1)
            self.last_update = time.time()
            nv = Vector([0,0,0])
            sx,sy,sz = self.get_sight_vector()*self.SPEED
            if self.action_states["for"]:
                nv += ( sx,0, sz)
            if self.action_states["back"]:
                nv += (-sx,0,-sz)
            if self.action_states["right"]:
                nv += (-sz,0, sx)
            if self.action_states["left"]:
                nv += ( sz,0,-sx)
            if self.onground():
                s = 0.5*self.SLIDING**dt
                self.velocity *= (1,0,1) #M# stop falling
                if self.action_states["jump"]:
                    self.velocity += (0,self.JUMPSPEED,0)
            else:
                s = 0.5*self.AIRRESISTANCE**dt
                self.velocity -= Vector([0,1,0])*self.GRAVITY*dt
            sv = s*Vector([1,0,1])+(0,1,0) #no slowing down in y
            self.velocity = sv*self.velocity + ((1,1,1)-sv)*nv
            
            steps = int(math.ceil(max(map(abs,self.velocity*dt))*10)) # 10 steps per block
            pos = self.position
            for step in range(steps):
                for i in range(DIMENSION):
                    mask          = Vector([int(i==j) for j in range(DIMENSION)])
                    inverted_mask = Vector([int(i!=j) for j in range(DIMENSION)])
                    new = pos + self.velocity*dt*mask*(1.0/steps)
                    if self.collide_difference(new,pos):
                        self.velocity *= inverted_mask
                    else:
                        pos = new
            self.set_position(pos)

def main(socket_server=None):
    with Game([simple_terrain_generator],playerclass=MC_PLAYER,socket_server=socket_server) as g:
        while True:
            g.update()
            for player in g.get_players():
                player.update()
            if not g.get_players():
                time.sleep(0.5)
            time.sleep(0.01) #wichtig damit das threading Zeug klappt
            
def singleplayer_client_thread(socket_client):
    import voxelengine.multiplayer.client as client
    client.main(socket_client)
    thread.interrupt_main()

if __name__ == "__main__":
    if select(["open server","play alone"])[0]:
        #Singleplayer
        import voxelengine.multiplayer.local_connection as local_connection
        connector = local_connection.Connector()
        try:
            thread.start_new_thread(singleplayer_client_thread,(connector.client,))
            main(connector.server)
        except KeyboardInterrupt:
            print "window closed"
    else:
        #Multiplayer
        main()
