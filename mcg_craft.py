from voxelengine import *
from noise import f4 as heightfunction

#TODO:
# server menu: open/new(enter name) save(select file to save to)/exit save/dontsave
# make sliding depend on block?

GRAVITY = 35
AIRRESISTANCE = 0.9
SLIDING = 0.001

def init_player(player):
    player.velocity = Vector([0,0,0])
    player.flying = False
    player.last_update = time.time()

    player.SPEED = 5
    player.JUMPSPEED = 10
    player.RENDERDISTANCE = 8
    
    height = 1.8
    eye_level = 1.6
    width = 0.4
    player.HITBOX = [(dx,dy,dz) for dx in (width,-width)
                                for dy in (height-eye_level,-eye_level)
                                for dz in (width,-width)]

def onground(player):
    for relpos in player.HITBOX:
        block_pos = (player.position+relpos+(0,-0.2,0)).normalize()
        if player.world[block_pos] != BLOCK_ID_BY_NAME["AIR"]:
            return True
    return False

def collide(player,position):
    blocks = set()
    for relpos in player.HITBOX:
        block_pos = (position+relpos).normalize()
        if player.world[block_pos] != BLOCK_ID_BY_NAME["AIR"]:
            blocks.add(block_pos)
    return blocks

def collide_difference(player,new_position,previous_position):
    """return blocks player collides with excluding the ones he already collides with"""
    return collide(player,new_position).difference(collide(player,previous_position))

def update_player(player):
    if not player.is_active(): # freeze player if client doesnt respond
        return
    if player.was_pressed("right click"):
        v = player.get_focused_pos()[1]
        if v:
            player.world[v] = BLOCK_ID_BY_NAME["GRASS"]
            if v in collide(player,player.position):
                player.world[v] = BLOCK_ID_BY_NAME["AIR"]
    if player.was_pressed("left click"):
        v = player.get_focused_pos()[0]
        if v:
            player.world[v] = BLOCK_ID_BY_NAME["AIR"]

    if player.flying:
        if player.is_pressed("for"):
            player.set_position(player.position+player.get_sight_vector()*0.2)
        return
    
    dt = time.time()-player.last_update
    dt = min(dt,1) # min slows time down for players if server is pretty slow
    player.last_update = time.time()
    nv = Vector([0,0,0])
    sx,sy,sz = player.get_sight_vector()*player.SPEED
    if player.is_pressed("for"):
        nv += ( sx,0, sz)
    if player.is_pressed("back"):
        nv += (-sx,0,-sz)
    if player.is_pressed("right"):
        nv += (-sz,0, sx)
    if player.is_pressed("left"):
        nv += ( sz,0,-sx)
    if onground(player):
        s = 0.5*SLIDING**dt
        player.velocity *= (1,0,1) #M# stop falling
        if player.is_pressed("jump"):
            player.velocity += (0,player.JUMPSPEED,0)
    else:
        s = 0.5*AIRRESISTANCE**dt
        player.velocity -= Vector([0,1,0])*GRAVITY*dt
    sv = s*Vector([1,0,1])+(0,1,0) #no slowing down in y
    player.velocity = sv*player.velocity + ((1,1,1)-sv)*nv
    
    steps = int(math.ceil(max(map(abs,player.velocity*dt))*10)) # 10 steps per block
    pos = player.position
    for step in range(steps):
        for i in range(DIMENSION):
            mask          = Vector([int(i==j) for j in range(DIMENSION)])
            inverted_mask = Vector([int(i!=j) for j in range(DIMENSION)])
            new = pos + player.velocity*dt*mask*(1.0/steps)
            if collide_difference(player,new,pos):
                player.velocity *= inverted_mask
            else:
                pos = new
    player.set_position(pos)

terrain_generator = terrain_generator_from_heightfunc(heightfunction)

if __name__ == "__main__":
    multiplayer = not select(["open server","play alone"])[0]
    spawnpoint = (0,int(heightfunction(0,0)+2),0)

    w = World([terrain_generator])

    settings = {"spawnpoint" : (w,spawnpoint),
                "multiplayer": multiplayer,
                }

    with Game(**settings) as g:
        while not g.get_players():
            g.update()
            time.sleep(0.5) #wait for players to connect
        while g.get_players():
            g.update()
            for player in g.get_new_players():
                init_player(player)
            for player in g.get_players():
                update_player(player)
