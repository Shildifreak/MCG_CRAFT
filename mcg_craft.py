import os

from voxelengine import *
from noise import f4 as heightfunction

#TODO:
# server menu: open/new(enter name) save(select file to save to)/exit save/dontsave
# make sliding depend on block?

GRAVITY = 35
AIRRESISTANCE = 0.9
SLIDING = 0.001

height = 1.8
eye_level = 1.6
width = 0.4
PLAYER_HITBOX = [(dx,dy,dz) for dx in (width,-width)
                            for dy in (height-eye_level,-eye_level)
                            for dz in (width,-width)]

def init_player(player):
    player.entity.set_texture("PLAYER")
    player.flying = False

    player.SPEED = 5
    player.JUMPSPEED = 10
    player.RENDERDISTANCE = 40

    player.entity.hitbox = PLAYER_HITBOX
    player.entity.velocity = Vector([0,0,0])
    player.entity.last_update = time.time()

def onground(entity):
    for relpos in entity.hitbox:
        block_pos = (entity.position+relpos+(0,-0.2,0)).normalize()
        if entity.world.get_block_name(block_pos) != "AIR": #M# test for solidity instead
            return True
    return False

def collide(entity,position):
    """blocks entity would collide with if it was at position"""
    blocks = set()
    for relpos in entity.hitbox:
        block_pos = (position+relpos).normalize()
        if entity.world.get_block_name(block_pos) != "AIR": #s.onground
            blocks.add(block_pos)
    return blocks

def collide_difference(entity,new_position,previous_position):
    """return blocks entity would newly collide with if it moved from previous_position to new_position"""
    return collide(entity,new_position).difference(collide(entity,previous_position))

def update_player(player):
    pe = player.entity
    if not player.is_active(): # freeze player if client doesnt respond
        return
    if player.was_pressed("right click"):
        v = player.get_focused_pos()[1]
        if v:
            pe.world[v] = "GRASS"
            if v in collide(pe,pe.position):
                pe.world[v] = "AIR"
    if player.was_pressed("left click"):
        v = player.get_focused_pos()[0]
        if v:
            pe.world[v] = "AIR"

    if player.flying:
        if player.is_pressed("for"):
            pe.set_position(pe.position+pe.get_sight_vector()*0.2)
        return

    dt = time.time()-pe.last_update
    dt = min(dt,1) # min slows time down for players if server is pretty slow
    pe.last_update = time.time()
    nv = Vector([0,0,0])
    sx,sy,sz = pe.get_sight_vector()*player.SPEED
    if player.is_pressed("for"):
        nv += ( sx,0, sz)
    if player.is_pressed("back"):
        nv += (-sx,0,-sz)
    if player.is_pressed("right"):
        nv += (-sz,0, sx)
    if player.is_pressed("left"):
        nv += ( sz,0,-sx)
    if onground(pe):
        s = 0.5*SLIDING**dt
        pe.velocity *= (1,0,1) #M# stop falling
        if player.is_pressed("jump"):
            pe.velocity += (0,player.JUMPSPEED,0)
    else:
        s = 0.5*AIRRESISTANCE**dt
        pe.velocity -= Vector([0,1,0])*GRAVITY*dt
    sv = s*Vector([1,0,1])+(0,1,0) #no slowing down in y
    pe.velocity = sv*pe.velocity + ((1,1,1)-sv)*nv
    
    steps = int(math.ceil(max(map(abs,pe.velocity*dt))*10)) # 10 steps per block
    pos = pe.position
    for step in range(steps):
        for i in range(DIMENSION):
            mask          = Vector([int(i==j) for j in range(DIMENSION)])
            inverted_mask = Vector([int(i!=j) for j in range(DIMENSION)])
            new = pos + pe.velocity*dt*mask*(1.0/steps)
            if collide_difference(pe,new,pos):
                pe.velocity *= inverted_mask
            else:
                pos = new
    pe.set_position(pos)

terrain_generator = terrain_generator_from_heightfunc(heightfunction,1)

if __name__ == "__main__":
    load_setup(os.path.join(PATH,"setups","mc_setup.py"))

    multiplayer = select(["open server","play alone"])[0] == 0
    spawnpoint = (0,int(heightfunction(0,0)+2),0)

    w = World([terrain_generator],spawnpoint=spawnpoint)

    def i_f(player):
        w.spawn_player(player)
        init_player(player)

    settings = {"init_function" : i_f,
                "multiplayer": multiplayer,
                }

    with Game(**settings) as g:
        while not g.get_players():
            g.update()
            time.sleep(0.5) #wait for players to connect
        while g.get_players():
            g.update()
            for player in g.get_players():
                update_player(player)
