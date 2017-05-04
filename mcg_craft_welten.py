import os,sys,math

sys.path.append("Welten")

from voxelengine import *
import random

#TODO:
# server menu: open/new(enter name) save(select file to save to)/exit save/dontsave
# make sliding depend on block?

GRAVITY = 35
AIRRESISTANCE = 5
SLIDING = 0.001
schafe = []

def floatrange(a,b):
    return [i+a for i in range(0, int(math.ceil(b-a))) + [b-a]]

def get_hitbox(width,height,eye_level):
    return [(dx,dy,dz) for dx in floatrange(-width,width)
                       for dy in floatrange(-eye_level,height-eye_level)
                       for dz in floatrange(-width,width)]
    
def init_player(player):
    player.entity.set_texture("PLAYER")
    player.flying = False

    player.RENDERDISTANCE = 20

    player.entity.SPEED = 10
    player.entity.JUMPSPEED = 10
    player.entity.hitbox = get_hitbox(0.4, 1.8, 1.6)
    player.entity.velocity = Vector([0,0,0])
    player.entity.last_update = time.time()

"""def init_schaf(world):
    schaf = Entity()
    schaf.set_texture("SCHAF")
    schaf.SPEED = 5
    schaf.JUMPSPEED = 10
    schaf.hitbox = get_hitbox(0.6,1.5,0.8)
    hat_position = False
    while not hat_position:
        x = random.randint(-40,40)
        y = random.randint(-40,40)
        z = random.randint(-40,40)
        schaf.set_position((x,y,z),world)
        if world.get_block_name((x,y-2,z)) != "AIR" and not collide(schaf,Vector((x,y,z))):
            hat_position = True
    schaf.velocity = Vector([0,0,0])
    schaf.last_update = time.time()
    schafe.append(schaf)"""
def init_schaf(world):
    schaf = Entity()
    schaf.set_texture("SCHAF")
    schaf.SPEED = 5
    schaf.JUMPSPEED = 20
    schaf.hitbox = get_hitbox(0.6,1.5,1)
    has_position = False
    while not has_position:
        x = random.randint(-40,40)
        z = random.randint(-40,40)
        y = random.randint(-40,40)
        #y = grashoehe(x,z) + 2
#        print x," ",y," ",z
        schaf.set_position((x,y,z),world)
        if world.get_block_name((x,y-2,z)) != "AIR" and len(collide_and_is_in(schaf,Vector((x,y,z)))) == 0:
#        if onground(schaf):
            has_position = True
    schaf.velocity = Vector([0,0,0])
    schaf.last_update = time.time()
    schaf.forward = False
    schaf.turn = 0
    schaf.nod = False
    schafe.append(schaf)


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

def collide_and_is_in(entity,position):
    #M# merge with normal collide
    """blocks entity would collide with and would be in if it was at position"""
    if entity.world.get_block_name(position.normalize()) != "AIR":
        blocks = collide(entity,position)
        blocks.add(position.normalize())
        return blocks
    return collide(entity,position)

def horizontal_move(entity,jump):
    if onground(entity):
        s = 0.5*SLIDING**entity.dt
        entity.velocity *= (1,0,1) #M# stop falling
        if jump:
            entity.velocity += (0,entity.JUMPSPEED,0)
    else:
        s = 0.5*AIRRESISTANCE**entity.dt
        entity.velocity -= Vector([0,1,0])*GRAVITY*entity.dt
    sv = Vector([s,1,s]) #no slowing down in y
    entity.velocity *= sv
    return sv

def update_dt(entity):
    entity.dt = time.time()-entity.last_update
    entity.dt = min(entity.dt,1) # min slows time down for players if server is pretty slow
    entity.last_update = time.time()

def update_position(entity):
    steps = int(math.ceil(max(map(abs,entity.velocity*entity.dt))*10)) # 10 steps per block
    pos = entity.position
    for step in range(steps):
        for i in range(DIMENSION):
            mask          = Vector([int(i==j) for j in range(DIMENSION)])
            inverted_mask = Vector([int(i!=j) for j in range(DIMENSION)])
            new = pos + entity.velocity*entity.dt*mask*(1.0/steps)
            if collide_difference(entity,new,pos):
                entity.velocity *= inverted_mask
            else:
                pos = new
    if pos != entity.position:
        entity.set_position(pos)

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
    update_dt(pe)
    
    nv = Vector([0,0,0])
    sx,sy,sz = pe.get_sight_vector()*pe.SPEED
    if player.is_pressed("for"):
        nv += ( sx,0, sz)
    if player.is_pressed("back"):
        nv += (-sx,0,-sz)
    if player.is_pressed("right"):
        nv += (-sz,0, sx)
    if player.is_pressed("left"):
        nv += ( sz,0,-sx)

    sv = horizontal_move(pe,player.is_pressed("jump"))

    
    pe.velocity += ((1,1,1)-sv)*nv
    update_position(pe)

def update_schaf(schaf):
    r = random.randint(0,99)
    if r < 1:
        schaf.turn = -5
        schaf.nod = False
    elif r < 2:
        schaf.turn = 5
        schaf.nod = False
    elif r < 3:
        schaf.forward = True
        schaf.turn = 0
        schaf.nod = False
    elif r < 5:
        schaf.forward = False
        schaf.nod = False
    elif r < 7:
        schaf.forward = False
        schaf.turn = 0
        schaf.nod = True
    
    
    update_dt(schaf)
    nv = Vector([0,0,0])
    sx,sy,sz = schaf.get_sight_vector()*schaf.SPEED
    if schaf.forward:
        nv += (sx,0,sz)
#    if len(collide_and_is_in(schaf,schaf.position)) != 0:
    jump = False
#    else:
#        jump = False
    sv = horizontal_move(schaf,jump)
    schaf.velocity += ((1,1,1)-sv)*nv
    update_position(schaf)
    if schaf.turn:
        y,p = schaf.rotation
        schaf.set_rotation(y+schaf.turn,p)

def grashoehe(x,z):
    return int(heightfunction(x,z))#int(5*math.sin(x/5.0)+5*math.sin(z/5.0)+5*math.sin(x/5.0+z/5.0))

def erdhoehe(x,z):
    return grashoehe(x,z)-1

def steinhoehe(x,z):
    return grashoehe(x,z)-3

chunksize = 2**setup["CHUNKSIZE"]
def baum_function(chunk):
    chunkpos = chunk.position*chunksize
    baumzahl = random.randint(0,1)
    for i in range(3):
        dx = random.choice(range(chunksize))
        dz = random.choice(range(chunksize))
        baumhoehe = random.randint(3,5)
        x = chunkpos[0] + dx
        z = chunkpos[2] + dz
        y = grashoehe(x,z)
        if 0 <= y-chunkpos[1] < chunksize:
            for dy in range(1,baumhoehe):
                chunk.set_block(Vector((x,y+dy,z)),"HOLZ")
            for dx in range(-1,2):
                for dz in range(-1,2):
                    for dy in range(3):
                        chunk.set_block(Vector((x+dx,y+dy+baumhoehe,z+dz)),"LAUB")

if __name__ == "__main__":
    load_setup(os.path.join(PATH,"setups","mc_setup.py"))

    multiplayer = select(["open server","play alone"])[0] == 0
    worldtypes = os.listdir("Welten")
    worldtypes = [x[:-3] for x in worldtypes if x.endswith(".py")]
    worldtype = select(worldtypes)[1]
    worldmod = __import__(worldtype)

    w = World(spawnpoint=(0,20,0))
    worldmod.init(w)

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
        i = 0
        while g.get_players():
            print "loop", i; i += 1
            g.update()
            for player in g.get_players():
                update_player(player)
            for schaf in schafe:
                #schaf.set_position(schaf.position + (0,0.01,0))
                update_schaf(schaf)
                pass
            if len(schafe) < 3:
                init_schaf(w)
