import os,sys,math

sys.path.append("Welten")
sys.path.append(os.path.join("Welten","structures"))

from voxelengine import *
import resources
import random

#TODO:
# server menu: open/new(enter name) save(select file to save to)/exit save/dontsave
# make sliding depend on block?

CHUNKSIZE = 4 # (in bit -> length is 2**CHUNKSIZE, so 4bit means the chunk has a size of 16x16x16 blocks)
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
    player.entity["texture"] = "PLAYER"
    player.set_focus_distance(8)

    player.flying = False
    player.RENDERDISTANCE = 8

    player.entity["SPEED"] = 10
    player.entity["JUMPSPEED"] = 10
    player.entity["hitbox"] = get_hitbox(0.4, 1.8, 1.6)
    player.entity["velocity"] = Vector([0,0,0])
    player.entity["last_update"] = time.time()
    player.entity["inventory"] = []
    player.entity["left_hand"] = {"id":"AIR"}
    player.entity["right_hand"] = {"id":"minecraft:grass"}


def init_schaf(world):
    schaf = Entity()
    schaf["texture"] = "SCHAF"
    schaf["SPEED"] = 5
    schaf["JUMPSPEED"] = 10
    schaf["hitbox"] = get_hitbox(0.6,1.5,1)
    schaf.set_world(world,(0,0,0))
    while True:
        x = random.randint(-40,40)
        z = random.randint(-10,10)
        y = random.randint(-40,40)
        if world.get_block((x,y-2,z)) != "AIR" and len(collide(schaf,Vector((x,y,z)))) == 0:
            break
    schaf["position"] = (x,y,z)
    schaf["velocity"] = Vector([0,0,0])
    schaf["last_update"] = time.time()
    schaf["forward"] = False
    schaf["turn"] = 0
    schaf["nod"] = False
    schafe.append(schaf)

def onground(entity):
    return bool_collide_difference(entity,entity["position"]+(0,-0.2,0),entity["position"])

def collide(entity,position):
    global debug_counter_2
    """blocks entity would collide with if it was at position"""
    blocks = set()
    for relpos in entity["hitbox"]:
        debug_counter_2 += 1
        block_pos = (position+relpos).normalize()
        if entity.world.get_block(block_pos) != "AIR": #s.onground
            blocks.add(block_pos)
    return blocks

Entity.collide = collide

def potential_collide_blocks(entity,position):
    blocks = set()
    for relpos in entity["hitbox"]:
        block_pos = (position+relpos).normalize()
        blocks.add(block_pos)
    return blocks


def collide_difference(entity,new_position,previous_position):
    """return blocks entity would newly collide with if it moved from previous_position to new_position"""
    return collide(entity,new_position).difference(collide(entity,previous_position))

def bool_collide_difference(entity,new_position,previous_position):
    global debug_counter_2
    for block in potential_collide_blocks(entity,new_position).difference(potential_collide_blocks(entity,previous_position)):
        debug_counter_2 += 1
        if entity.world.get_block(block) != "AIR":
            return True
    return False
    


def horizontal_move(entity,jump):
    if onground(entity):
        s = 0.5*SLIDING**entity.dt
        entity["velocity"] *= (1,0,1) #M# stop falling
        if jump:
            entity["velocity"] += (0,entity["JUMPSPEED"],0)
    else:
        s = 0.5*AIRRESISTANCE**entity.dt
        entity["velocity"] -= Vector([0,1,0])*GRAVITY*entity.dt
    sv = Vector([s,1,s]) #no slowing down in y
    entity["velocity"] *= sv
    return sv

def update_dt(entity):
    entity.dt = time.time()-entity["last_update"]
    entity.dt = min(entity.dt,1) # min slows time down for players if server is pretty slow
    entity["last_update"] = time.time()

def update_position(entity):
    steps = int(math.ceil(max(map(abs,entity["velocity"]*entity.dt))*10)) # 10 steps per block
    pos = entity["position"]
    for step in range(steps):
        for i in range(DIMENSION):
            mask          = Vector([int(i==j) for j in range(DIMENSION)])
            inverted_mask = Vector([int(i!=j) for j in range(DIMENSION)])
            new = pos + entity["velocity"]*entity.dt*mask*(1.0/steps)
            if bool_collide_difference(entity,new,pos):
                entity["velocity"] *= inverted_mask
            else:
                pos = new
    if pos != entity["position"]:
        entity["position"] = pos

def update_player(player):
    pe = player.entity
    if not player.is_active(): # freeze player if client doesnt respond
        return

    #           left click      right click
    # no shift  mine block      activate block
    # shift     use l item      use r. item
    handstuff = (("right click","right_hand",lambda block:block.activated),
                 ("left click", "left_hand", lambda block:block.mined))
    for event_name, hand_name, primary_action in handstuff:
        if player.was_pressed(event_name):
            pos, face = player.get_focused_pos()
            do_item_action = True
            if pos and not player.is_pressed("shift"):
                block = pe.world[pos]
                do_item_action = primary_action(resources.blocks[block](pe.world,pos))(pe)
            if do_item_action:
                item_data = pe[hand_name]
                item = resources.items[item_data["id"]](item_data)
                if pos:
                    item.use_on_block(pe,pos,face)
                else:
                    item.use_on_air(pe)            

    if player.flying:
        if player.is_pressed("for"):
            pe.set_position(pe["position"]+pe.get_sight_vector()*0.2)
        return
    update_dt(pe)
    
    nv = Vector([0,0,0])
    sx,sy,sz = pe.get_sight_vector()*pe["SPEED"]
    if player.is_pressed("for"):
        nv += ( sx,0, sz)
    if player.is_pressed("back"):
        nv += (-sx,0,-sz)
    if player.is_pressed("right"):
        nv += (-sz,0, sx)
    if player.is_pressed("left"):
        nv += ( sz,0,-sx)

    sv = horizontal_move(pe,player.is_pressed("jump"))

    
    pe["velocity"] += ((1,1,1)-sv)*nv
    update_position(pe)

def update_schaf(schaf):
    r = random.randint(0,200)
    if r < 1:
        schaf["turn"] = -5
        schaf["nod"] = False
    elif r < 2:
        schaf["turn"] = 5
        schaf["nod"] = False
    elif r < 3:
        schaf["forward"] = True
        schaf["turn"] = 0
        schaf["nod"] = False
    elif r < 5:
        schaf["forward"] = False
        schaf["nod"] = False
    elif r < 7:
        schaf["forward"] = False
        schaf["turn"] = 0
        schaf["nod"] = True
    
    update_dt(schaf)
    nv = Vector([0,0,0])
    sx,sy,sz = schaf.get_sight_vector()
    if schaf["forward"]:
        nv += Vector((sx,0,sz))*schaf["SPEED"]
        jump = schaf.world.get_block((schaf["position"]+Vector((sx,-0.5,sz))).normalize()) != "AIR"
    else:
        jump = not random.randint(0,2000)
    sv = horizontal_move(schaf,jump)
    schaf["velocity"] += ((1,1,1)-sv)*nv
    update_position(schaf)
    y, p = schaf["rotation"]
    dy = schaf["turn"]
    dp = -schaf["nod"]*50 - p
    if dy or dp:
        schaf["rotation"] = y+dy, p+dp
        

debug_counter_1 = 1
debug_counter_2 = 1

class MCGCraftWorld(World):
    def __init__(self,*args,**kwargs):
        World.__init__(self,*args,**kwargs)
        self.set_block_buffer = {}
        self.block_updates = []

    def schedule_blocks(self,positions,blocks,callback):
        pass

    #def set_block(self,position,block):
    #    l = self.set_block_buffer.setdefault(position,[])
    #    l.append(block)

    def tick(self):
        for position, blocklist in self.set_block_buffer.items():
            if len(blocklist) == 1:
                World.set_block(self,position,blocklist[0])
            elif len(blocklist) > 1:
                print("can't set multiple block at one tick to the same position")
                #M# drop 'em!

if __name__ == "__main__":
    multiplayer = select(["open server","play alone"])[0] == 0
    worldtypes = os.listdir("Welten")
    worldtypes = [x[:-3] for x in worldtypes if x.endswith(".py")]
    worldtype = select(worldtypes)[1]
    worldmod = __import__(worldtype)

    w = MCGCraftWorld(worldmod.terrain_generator,spawnpoint=worldmod.spawnpoint,chunksize=CHUNKSIZE)
    worldmod.init(w)

    def i_f(player):
        w.spawn_player(player)
        init_player(player)

    settings = {"init_function" : i_f,
                "multiplayer": multiplayer,
                "renderlimit": False, # whether to show just the chunks in renderdistance (True) or all loaded chunks (False)
                "suggested_texturepack" : "mcgcraft-standart",
                }

    with Game(**settings) as g:
        while not g.get_players():
            g.update()
            time.sleep(0.5) #wait for players to connect
        while g.get_players():
            #print "counter", debug_counter_1, debug_counter_2, debug_counter_2//debug_counter_1; debug_counter_1 += 1
            g.update()
            for player in g.get_players():
                update_player(player)
            for schaf in schafe:
                update_schaf(schaf)
                pass
            if len(schafe) < 5:
                init_schaf(w)
