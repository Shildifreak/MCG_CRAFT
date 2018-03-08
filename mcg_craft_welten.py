import os,sys,math

sys.path.append("Welten")
sys.path.append(os.path.join("Welten","structures"))

from voxelengine import *
import resources
import random, itertools

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

def display_item(player,name,item,position,size,align):
    w, h = size
    player.set_hud(name+"_bgbox","GLAS",position+Vector((0,0,-0.01)),0,size,align)
    player.set_hud(name,item["id"],position,0,Vector(size)*0.8,align)
    player.set_hud(name+"_count","/"+str(item.get("count","")),position+Vector((0.6*w,-0.6*h,0.01)),0,(0,0),align)
Player.display_item = display_item
def undisplay_item(player,name):
    for suffix in ("_bgbox","","_count"):
        player.del_hud(name+suffix)
Player.undisplay_item = undisplay_item

class InventoryDisplay():
    def __init__(self,player):
        self.player = player
        self.is_open = False #Full inventory or only hotbar
        self.inventory = self.player.entity["inventory"]
        self.foreign_inventory = None
        self.current_pages = [0,0]
        self.inventory.register_callback(self.callback)

    def callback(self,inventory):
        self.display()

    def _calculate_index(self,k,row,col):
        return self.current_pages[k]*7 + row*7 + col

    def display(self):
        size = (0.1,0.1)
        rows = 4# if self.foreign_inventory else 9
        for k, inventory in enumerate((self.inventory, self.foreign_inventory)):
            for col in range(7):
                for row in range(rows):
                    name = "inventory:(%i,%i,%i)" %(k,col,row)
                    if inventory and (self.is_open or k + row == 0):
                        i = self._calculate_index(k,row,col)
                        if len(inventory) > i:
                            item = inventory[i]
                        else:
                            item = {"id":"AIR"}
                        x = 0.2*(col - 3)
                        y = 0.2*(row) + k - 0.8
                        position = (x,y,0)
                        self.player.display_item(name,item,position,size,INNER|CENTER)
                    else:
                        self.player.undisplay_item(name)            
                       # print "hop",k,row,col,inventory
            if inventory and self.is_open:
                self.player.set_hud("inventory:(%s,%s)" %(k,-1),"ARROW",(0.8,k-0.6,0),0,size,INNER|CENTER)
                self.player.set_hud("inventory:(%s,%s)" %(k,+1),"ARROW",(0.8,k-0.4,0),0,size,INNER|CENTER)
            else:
                self.player.del_hud("inventory:(%s,%s)" %(k,-1))
                self.player.del_hud("inventory:(%s,%s)" %(k,+1))

    def open(self,foreign_inventory = None):
        if self.is_open:
            self.close()
        self.is_open = True
        self.player.focus_hud()
        self.current_pages = [0,0]
        if foreign_inventory != None:
            self.foreign_inventory = foreign_inventory
            if foreign_inventory != self.inventory:
                foreign_inventory.register_callback(self.callback,False)
        self.display()

    def close(self):
        if not self.is_open:
            return
        self.is_open = False
        if self.foreign_inventory != None:
            if self.foreign_inventory != self.inventory:
                self.foreign_inventory.unregister_callback(self.callback)
            self.foreign_inventory = None
        self.display()
    
    def toggle(self):
        if self.is_open:
            self.close()
        else:
            self.open()
            
    def handle_click(self,event):
        if event.startswith("left"):
            hand = "left_hand"
        if event.startswith("right"):
            hand = "right_hand"
        args = event.rsplit("(",1)[1].split(")",1)[0].split(",")
        if len(args) == 3:
            k, col, row = map(int,args)
            inventory = self.inventory if k==0 else self.foreign_inventory
            index = self._calculate_index(k,row,col)
            self.swap(inventory,index,hand)
        else:
            k, direction = map(int,args)
            inventory = self.inventory if k==0 else self.foreign_inventory
            self.current_pages[k] = max(0,self.current_pages[k] + direction)
            self.display()
            
    
    def swap(self,inventory,index,hand):
        x, y = self.player.entity[hand], inventory[index]
        x.parent = None
        y.parent = None
        self.player.entity[hand], inventory[index] = y, x

def init_player(player):
    player.set_focus_distance(8)

    player.flying = False
    player.RENDERDISTANCE = 8

    player.entity["SPEED"] = 10
    player.entity["FLYSPEED"] = 0.2
    player.entity["JUMPSPEED"] = 10
    player.entity["texture"] = "PLAYER"
    player.entity["hitbox"] = get_hitbox(0.4, 1.8, 1.6)
    player.entity["velocity"] = Vector([0,0,0])
    player.entity["last_update"] = time.time()
    player.entity["inventory"] = [{"id":"HERZ"},{"id":"GESICHT"}]
    player.entity["left_hand"] = {"id":"CHEST"}
    player.entity["right_hand"] = {"id":"GRASS","count":64}
    player.entity["health"] = 10
    player.entity["open_inventory"] = False #set player.entity.foreign_inventory then trigger opening by setting this attribute
    player.entity["lives"] = 9
    

    # inventory stuff
    for i in range(60):
        player.entity["inventory"].append({"id":"DIRT","count":i})

    player.inventory_display = InventoryDisplay(player)

    def open_inventory_callback(boolean):
        if boolean:
            player.inventory_display.open(player.entity.foreign_inventory)
            player.entity.foreign_inventory = None
        else:
            player.inventory_display.close()
    player.entity.register_item_callback(open_inventory_callback,"open_inventory")

    def update_left_hand_image(item):
        player.display_item("left_hand",item,(-0.8,-0.8,0.5),(0.1,0.1),BOTTOM|LEFT)
    def update_right_hand_image(item):
        player.display_item("right_hand",item,(0.8,-0.8,0.5),(0.1,0.1),BOTTOM|RIGHT)
    def update_inventar(inventar):
        pass
    def update_lives(lives):
        for x in range(lives):
            player.set_hud("heart"+str(x),"HERZ",Vector((-0.97+x/10.0,0.95,0)),0,(0.05,0.05),INNER|CENTER)
    player.entity.register_item_callback(update_left_hand_image,"left_hand")
    player.entity.register_item_callback(update_right_hand_image,"right_hand")
    player.entity.register_item_callback(update_lives,"lives")
    

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
                block_object = pe.world.get_block_object(pos)
                do_item_action = primary_action(block_object)(pe, face)
            if do_item_action:
                item_data = pe[hand_name]
                item = resources.items[item_data["id"]](item_data)
                if pos:
                    item.use_on_block(pe,pos,face)
                else:
                    item.use_on_air(pe)            

    if player.was_pressed_set:
        print player.was_pressed_set

    if player.was_pressed("fly"):
        player.flying = not player.flying
    if player.was_pressed("inv"):
        player.inventory_display.toggle()
    for pressed in player.was_pressed_set:
        if pressed.startswith("left clicked inventory") or pressed.startswith("right clicked inventory"):
            player.inventory_display.handle_click(pressed)

    # Movement
    update_dt(pe)
    
    nv = Vector([0,0,0])
    sx,sy,sz = pe.get_sight_vector()
    if player.is_pressed("for"):
        nv += ( sx,0, sz)
    if player.is_pressed("back"):
        nv += (-sx,0,-sz)
    if player.is_pressed("right"):
        nv += (-sz,0, sx)
    if player.is_pressed("left"):
        nv += ( sz,0,-sx)

    # Flying
    if player.flying:
        if player.is_pressed("jump"):
            nv += (0, 1, 0)
        if player.is_pressed("shift"):
            nv -= (0, 1, 0)
        pe["position"] += nv*pe["FLYSPEED"]
        return

    # Walking
    sv = horizontal_move(pe,player.is_pressed("jump"))

    pe["velocity"] += ((1,1,1)-sv)*nv*pe["SPEED"]
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
        self.changed_blocks = []

    def get_block_object(self,position):
        return resources.blocks[self[position].rsplit(":",1)[0]](self,position)

    def set_block(self,position,block):
        if not isinstance(position,Vector):
            position = Vector(position)
        World.set_block(self, position, block)
        self.changed_blocks.append(position)

    def tick(self):
        # do timestep for blockupdates -> first compute all then update all, so update order doesn't matter
        new_blocks = [] #(position,block)
        block_updates = ((position-face, face) for position in self.changed_blocks
                                               for face in ((-1,0,0),(1,0,0),(0,-1,0),(0,0,-1),(0,0,-1),(0,0,1)))
        for position, group in itertools.groupby(block_updates,lambda x:x[0]):
            faces = [x[1] for x in group]
            new_block = self.get_block_object(position).block_update(faces)
            if new_block:
                new_blocks.append((position,new_block))
        self.changed_blocks = []
        for position, block in new_blocks:
            self[position] = block

if __name__ == "__main__":
    multiplayer = select(["open server","play alone"])[0] == 0
    worldtypes = os.listdir("Welten")
    worldtypes = [x[:-3] for x in worldtypes if x.endswith(".py")]
    worldtype = select(worldtypes)[1]
    worldmod = __import__(worldtype)

    w = MCGCraftWorld(worldmod.terrain_generator,spawnpoint=worldmod.spawnpoint,chunksize=CHUNKSIZE)
    worldmod.init(w)
    w.changed_blocks = []
    
    def i_f(player):
        w.spawn_player(player)
        init_player(player)

    renderlimit = not multiplayer #fast loading for playing alone, hole world for multiplayer
    settings = {"init_function" : i_f,
                "multiplayer": multiplayer,
                "renderlimit": renderlimit, # whether to show just the chunks in renderdistance (True) or all loaded chunks (False)
                "suggested_texturepack" : "mcgcraft-standart",
                }

    with Game(**settings) as g:
        while not g.get_players():
            g.update()
            time.sleep(0.5) #wait for players to connect
        while g.get_players():
            #print "counter", debug_counter_1, debug_counter_2, debug_counter_2//debug_counter_1; debug_counter_1 += 1
            g.update()
            w.tick()
            for player in g.get_players():
                update_player(player)
            for schaf in schafe:
                update_schaf(schaf)
                pass
            if len(schafe) < 0:
                init_schaf(w)
