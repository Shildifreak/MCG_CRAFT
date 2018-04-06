import os, sys, thread, ast
import math, random, itertools
import getpass

sys.path.append("Welten")
sys.path.append(os.path.join("Welten","structures"))
sys.path.append("gui")

from voxelengine import *
import resources
import appdirs

#TODO:
# server menu: open/new(enter name) save(select file to save to)/exit save/dontsave
# make sliding depend on block?

CHUNKSIZE = 4 # (in bit -> length is 2**CHUNKSIZE, so 4bit means the chunk has a size of 16x16x16 blocks)
GRAVITY = 35
AIRRESISTANCE = 5
SLIDING = 0.001
SCHAFLIMIT = 0
schafe = []

def floatrange(a,b):
    return [i+a for i in range(0, int(math.ceil(b-a))) + [b-a]]

def get_hitbox(width,height,eye_level):
    return [(dx,dy,dz) for dx in floatrange(-width,width)
                       for dy in floatrange(-eye_level,height-eye_level)
                       for dz in floatrange(-width,width)]

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
                        item = inventory.get(i,None)
                        if item:
                            x = 0.2*(col - 3)
                            y = 0.2*(row) + k - 0.8
                            position = (x,y,0)
                            self.player.display_item(name,item,position,size,INNER|CENTER)
                            continue
                    self.player.undisplay_item(name)            
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


class Player(Player):
    RENDERDISTANCE = 10
    def init(self): #called in init_function after world has created entity for player
        self.set_focus_distance(8)

        self.flying = False

        self.entity["SPEED"] = 10
        self.entity["FLYSPEED"] = 0.2
        self.entity["JUMPSPEED"] = 10
        self.entity["texture"] = "PLAYER"
        self.entity["hitbox"] = get_hitbox(0.4, 1.8, 1.6)
        self.entity["velocity"] = Vector([0,0,0])
        self.entity["last_update"] = time.time()
        self.entity["inventory"] = [{"id":"Setzling"},{"id":"HEBEL"},{"id":"WAND"},{"id":"BARRIER"},{"id":"LAMPOFF"},{"id":"TORCH"}]
        self.entity["left_hand"] = {"id":"CHEST"}
        self.entity["right_hand"] = {"id":"DOORSTEP","count":1}
        self.entity["health"] = 10
        self.entity["open_inventory"] = False #set player.entity.foreign_inventory then trigger opening by setting this attribute
        self.entity["lives"] = 9
        
        # inventory stuff
        for i in range(60):
            self.entity["inventory"].append({"id":"AIR","count":i})

        self.inventory_display = InventoryDisplay(self)

        def open_inventory_callback(boolean):
            if boolean:
                self.inventory_display.open(self.entity.foreign_inventory)
                self.entity.foreign_inventory = None
            else:
                self.inventory_display.close()
        self.entity.register_item_callback(open_inventory_callback,"open_inventory")

        def update_left_hand_image(item):
            self.display_item("left_hand",item,(-0.8,-0.8,0.5),(0.1,0.1),BOTTOM|LEFT)
        def update_right_hand_image(item):
            self.display_item("right_hand",item,(0.8,-0.8,0.5),(0.1,0.1),BOTTOM|RIGHT)
        def update_inventar(inventar):
            pass
        def update_lives(lives):
            for x in range(lives):
                self.set_hud("heart"+str(x),"HERZ",Vector((-0.97+x/10.0,0.95,0)),0,(0.05,0.05),INNER|CENTER)
        self.entity.register_item_callback(update_left_hand_image,"left_hand")
        self.entity.register_item_callback(update_right_hand_image,"right_hand")
        self.entity.register_item_callback(update_lives,"lives")

    def update(self):
        pe = self.entity
        #if not self.is_active(): # freeze player if client doesnt respond
        #    return

        #           left click      right click
        # no shift  mine block      activate block
        # shift     use l item      use r. item
        handstuff = (("right click","right_hand",lambda block:block.activated),
                     ("left click", "left_hand", lambda block:block.mined))
        for event_name, hand_name, primary_action in handstuff:
            if self.was_pressed(event_name):
                pos, face = self.get_focused_pos()
                do_item_action = True
                if pos and not self.is_pressed("shift"):
                    do_item_action = primary_action(pe.world[pos])(pe, face)
                if do_item_action:
                    item_data = pe[hand_name]
                    item = resources.items[item_data["id"]](item_data)
                    if pos:
                        item.use_on_block(pe,pos,face)
                    else:
                        item.use_on_air(pe)            

        if self.was_pressed("fly"):
            self.flying = not self.flying
        if self.was_pressed("inv"):
            self.inventory_display.toggle()
        for pressed in self.was_pressed_set:
            if pressed.startswith("left clicked inventory") or pressed.startswith("right clicked inventory"):
                self.inventory_display.handle_click(pressed)

        # Movement
        pe.update_dt()
        
        nv = Vector([0,0,0])
        sx,sy,sz = pe.get_sight_vector()
        if self.is_pressed("for"):
            nv += ( sx,0, sz)
        if self.is_pressed("back"):
            nv += (-sx,0,-sz)
        if self.is_pressed("right"):
            nv += (-sz,0, sx)
        if self.is_pressed("left"):
            nv += ( sz,0,-sx)

        # Flying
        if self.flying:
            if self.is_pressed("jump"):
                nv += (0, 1, 0)
            if self.is_pressed("shift"):
                nv -= (0, 1, 0)
            pe["position"] += nv*pe["FLYSPEED"]
            return

        # Walking
        sv = pe.horizontal_move(self.is_pressed("jump"))

        pe["velocity"] += ((1,1,1)-sv)*nv*pe["SPEED"]
        pe.update_position()

    def do_random_ticks(player):
        radius = 10
        ticks = 5
        for a in range(ticks):
            dp = (random.gauss(0,radius),random.gauss(0,radius),random.gauss(0,radius))
            block = player.entity.world.get_block((player.entity["position"]+dp).normalize(),load_on_miss = False)
            if block:
                block.random_ticked()

    def display_item(self,name,item,position,size,align):
        w, h = size
        self.set_hud(name+"_bgbox","GLAS",position+Vector((0,0,-0.01)),0,size,align)
        self.set_hud(name,item["id"],position,0,Vector(size)*0.8,align)
        self.set_hud(name+"_count","/"+str(item.get("count","")),position+Vector((0.6*w,-0.6*h,0.01)),0,(0,0),align)

    def undisplay_item(self,name):
        for suffix in ("_bgbox","","_count"):
            self.del_hud(name+suffix)

class Entity(Entity):
    def onground(entity):
        return entity.bool_collide_difference(entity["position"]+(0,-0.2,0),entity["position"])

    def collide(entity,position):
        """blocks entity would collide with if it was at position"""
        blocks = set()
        for relpos in entity["hitbox"]:
            block_pos = (position+relpos).normalize()
            if entity.world.get_block(block_pos).collides_with(entity): #s.onground
                blocks.add(block_pos)
        return blocks

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
        for block in entity.potential_collide_blocks(new_position).difference(entity.potential_collide_blocks(previous_position)):
            if entity.world.get_block(block).collides_with(entity):
                return True
        return False
    
    def horizontal_move(entity,jump): #M# name is misleading
        if entity.onground():
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
                if entity.bool_collide_difference(new,pos):
                    entity["velocity"] *= inverted_mask
                else:
                    pos = new
        if pos != entity["position"]:
            entity["position"] = pos
    
    def block_update(self):
        """called when block "near" entity is changed"""
        pass

class Schaf(Entity):
    def __init__(self, world):
        super(Schaf,self).__init__()

        self["texture"] = "SCHAF"
        self["SPEED"] = 5
        self["JUMPSPEED"] = 10
        self["hitbox"] = get_hitbox(0.6,1.5,1)
        self["sprint"] = 20
        self.set_world(world,(0,0,0))
        while True:
            x = random.randint(-40,40)
            z = random.randint(-10,10)
            y = random.randint(-40,40)
            block = world.get_block((x,y-2,z),load_on_miss = False)
            if block and block != "AIR" and len(self.collide(Vector((x,y,z)))) == 0:
                break
        self["position"] = (x,y,z)
        self["velocity"] = Vector([0,0,0])
        self["last_update"] = time.time()
        self["forward"] = False
        self["turn"] = 0
        self["nod"] = False
        schafe.append(self)

    def update(schaf):
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
        
        schaf.update_dt()
        nv = Vector([0,0,0])
        sx,sy,sz = schaf.get_sight_vector()
        if schaf["forward"]:
            nv += Vector((sx,0,sz))*schaf["SPEED"]
            jump = schaf.world.get_block((schaf["position"]+Vector((sx,-0.5,sz))).normalize()) != "AIR"
        else:
            jump = not random.randint(0,2000)
        sv = schaf.horizontal_move(jump)
        schaf["velocity"] += ((1,1,1)-sv)*nv
        schaf.update_position()
        y, p = schaf["rotation"]
        dy = schaf["turn"]
        dp = -schaf["nod"]*50 - p
        if dy or dp:
            schaf["rotation"] = y+dy, p+dp

class Block(Block):
    block_class = property(lambda self: resources.blocks[self["id"]])
    def __getattr__(self, name):
        #bc = resources.blocks[self["id"]]
        attr = getattr(self.block_class,name)
        if callable(attr):
            return attr.__get__(self)
        return attr
    def __getitem__(self, key):
        try:
            return super(Block, self).__getitem__(key)
        except KeyError:
            return self.block_class.defaults[key]
    def __setitem__(self, key, value):
        if value == self[key]:
            return
        if value == self.block_class.defaults.get(key,(value,)): #(value,) is always != value, so if there is no default this defaults to false
            super(Block,self).__delitem__(key)
        else:
            super(Block,self).__setitem__(key,value)
        self.world.changed_blocks.append(self.position)

blockread_counter = 0
class World(World):
    BlockClass = Block
    EntityClass = Entity
    def __init__(self,*args,**kwargs):
        super(World,self).__init__(*args,**kwargs)
        self.changed_blocks = []

    def get_block(self,position,*args,**kwargs):
        global blockread_counter
        blockread_counter += 1
        return super(World,self).get_block(position,*args,**kwargs)

    def set_block(self,position,block,*args,**kwargs):
        if not isinstance(position,Vector):
            position = Vector(position)
        super(World,self).set_block(position, block,*args,**kwargs)
        self.changed_blocks.append(position)

    def tick(self):
        # do entity updates
        if self.changed_blocks:
            for entity in self.get_entities(): #M# limited distance, not all?
                entity.block_update()
        # do timestep for blockupdates -> first compute all then update all, so update order doesn't matter
        new_blocks = [] #(position,block)
        block_updates = ((position-face, face) for position in self.changed_blocks
                                               for face in ((-1,0,0),(1,0,0),(0,-1,0),(0,0,-1),(0,0,-1),(0,0,1))) #M# ,(0,0,0)
        for position, group in itertools.groupby(block_updates,lambda x:x[0]):
            faces = [x[1] for x in group]
            new_block = self[position].block_update(faces)
            if new_block:
                new_blocks.append((position,new_block))
        self.changed_blocks = []
        for position, block in new_blocks:
            self[position] = block

class UI(object):
    def __init__(self, config, worldtypes):
        config["worldtype"] = select(worldtypes)[1]
        config["run"] = True
    def stats(self, name, value):
        print name, value

def zeitmessung(ts = [0]*200, t = [time.time()]):
    dt = time.time() - t[0]
    t[0] += dt
    dt = round(1/dt,2)
    ts.append(dt)
    ts.pop(0)
    ui.stats("dt",dt)
    ui.stats("min dt", min(ts))
    ui.stats("max dt", max(ts))

def gameloop():
    global w, g
    while not config["quit"]:
        #wait for config being ready to start
        if not config["run"]:
            time.sleep(0.1)
            continue #jump back to start of loop
        print "starting Game ..."
        worldmod = __import__(config["worldtype"])

        w = World(worldmod.terrain_generator,spawnpoint=worldmod.spawnpoint,chunksize=CHUNKSIZE,defaultblock=Block("AIR"))
        worldmod.init(w)
        w.changed_blocks = []
        
        def i_f(player):
            w.spawn_player(player)
            player.init()

        renderlimit = True #True: fast loading, False: whole world at once
        settings = {"init_function": i_f,
                    "renderlimit": True,#renderlimit, # whether to show just the chunks in renderdistance (True) or all loaded chunks (False)
                    "suggested_texturepack" : "mcgcraft-standart",
                    "PlayerClass" : Player,
                    "wait" : False,
                    "name" : config["name"],
                    }
        stats = {}
        with Game(**settings) as g:
            print "Game started"
            while config["run"]:
                if config["play"]:
                    config["play"] = False
                    g.launch_client()
                zeitmessung()
                #print blockread_counter
                blockread_counter = 0
                #
                g.update()
                w.tick()
                for player in g.get_players():
                    player.update()
                    player.do_random_ticks()
                for schaf in schafe:
                    schaf.update()
                if len(schafe) < SCHAFLIMIT:
                    Schaf(w)
        print "Game stopped"
    print "Server shut down"
    rememberconfig = config.copy()
    for key in ("run","play","quit"):
        rememberconfig.pop(key)
    with open(configfn,"w") as configfile:
        configfile.write(repr(rememberconfig))
    print "Config saved"
    
if __name__ == "__main__":
    config = {  "name"     : "%ss MCGCraft Server" %getpass.getuser(),
                "file"     : "",
                "worldtype": "Colorland",
                "whitelist": "127.0.0.1",
                "parole"   : "",
                "port"     : "",
                "run"      : False,
                "play"     : False,
                "quit"     : False,
             }
    configdir = appdirs.user_config_dir("MCGCraft","ProgrammierAG")
    configfn = os.path.join(configdir,"serversettings.py")
    if os.path.exists(configfn):
        with open(configfn,"r") as configfile:
            rememberedconfig = ast.literal_eval(configfile.read())
        config.update(rememberedconfig)
    elif not os.path.exists(configdir):
        os.makedirs(configdir)
        
    worldtypes = os.listdir("Welten")
    worldtypes = [x[:-3] for x in worldtypes if x.endswith(".py")]
    try:
        from tkgui import GUI as UI
    except ImportError as e:
        print "GUI not working cause of:\n",e
    ui = UI(config, worldtypes)
    if sys.flags.interactive:
        thread.start_new_thread(gameloop,())
    else:
        gameloop()
