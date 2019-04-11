#! /usr/bin/env python
#* encoding: utf-8 *#
from __future__ import print_function

if __name__ != "__main__":
    raise Warning("mcgcrafft.py should not be imported")

# hack der nur bei uns in der Schule funktioniert, damit mcgcraft mit python2 ausgeführt wird
import os, sys
if sys.version >= "3":
    os.system("C:\\Python27\\python.exe mcgcraft.py") 
    sys.exit(0)

# Imports
import sys, os, thread, ast, imp, inspect
import math, time, random, itertools, collections
import getpass

PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append("lib")
sys.path.append(os.path.join("resources","Welten","structures"))

import voxelengine
import appdirs
import resources

from shared import *

CHUNKSIZE = 4 # (in bit -> length is 2**CHUNKSIZE, so 4bit means the chunk has a size of 16x16x16 blocks)

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




class Player(voxelengine.Player):
    RENDERDISTANCE = 10
    def init(self): #called in init_function after world has created entity for player
        self.set_focus_distance(8)

        self.flying = False

        # just for testing:
        self.entity["inventory"] = [{"id":"Repeater"},{"id":"FAN"},{"id":"Setzling"},{"id":"HEBEL"},{"id":"WAND"},{"id":"BARRIER"},{"id":"LAMP"},{"id":"TORCH"},{"id":"Redstone","count":128},{"id":"CHEST"}]
        self.entity["left_hand"] = {"id":"DOORSTEP","count":1}
        self.entity["right_hand"] = {"id":"ROCKET"}

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
            #todo: fix!
            for x in range(lives,10):
                self.del_hud("heart"+str(x))
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
                
        get_block = lambda: pe.world[pos]
        def get_item():
            hand_name = {"left click": "left_hand", "right click":"right_hand"}[event_name]
            item_data = pe[hand_name]
            return resources.itemClasses[item_data["id"]](item_data)

        for event_name in ("left click", "right click"):
            if self.was_pressed(event_name):
                d_block, pos, face = self.get_focused_pos()
                d_entity, entity = self.get_focused_entity()

                # nothing to click on
                if (d_block == None) and (d_entity == None):
                    get_item().use_on_air(pe)
                    continue

                # click on block
                if (d_block != None) and ((d_entity == None) or (d_block < d_entity)):
                    actions = {"right click": (lambda:get_block().activated(pe, face),
                                               lambda:get_item().use_on_block(pe, pos, face)),
                               "left click" : (lambda:get_block().mined(pe, face),
                                               lambda:get_item().use_on_block(pe, pos, face))}[event_name]
                # click on entity
                else:
                    actions = {"right click": (lambda:get_item().use_on_entity(pe, entity),
                                               lambda:entity.right_clicked(pe)),
                               "left click" : (lambda:get_item().use_on_entity(pe, entity),
                                               lambda:entity.left_clicked(pe))}[event_name]
                action1, action2 = actions
                do_next = True if self.is_pressed("shift") else action1()
                if do_next:
                    action2()

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
            pe["position"] += nv*pe["FLYSPEED"]*pe.dt
            pe["velocity"] = (0,0,0)
            return

        # Walking
        sv = pe.horizontal_move(self.is_pressed("jump"))

        if self.was_released("for") or \
           self.was_released("back") or \
           self.was_released("right") or \
           self.was_released("left"):
            pe["velocity"] *= (0,1,0)

        pe["velocity"] += nv*pe["ACCELERATION"]
        l = pe["velocity"].length()
        if l > pe["SPEED"]:
            f = pe["SPEED"] / l
            pe["velocity"] *= (f,1,f)

        # save previous velocity and onground
        vy_vorher = pe["velocity"][1]
        onground_vorher = pe.onground()
        # update position
        pe.update_position()
        # see if player hit the ground and calculate damage
        if (not onground_vorher) and pe.onground():
            # Geschwindigkeit 20 entspricht etwa einer Fallhoehe von 6 Block, also ab 7 nimmt der Spieler Schaden
            schaden = (-vy_vorher) -20
            print(schaden)
            # HERZEN ANPASSEN
            if schaden >0:
                a = pe["lives"]
                b = pe["lives"] - 1

                pe["lives"] = b

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

class ValidTag(object):
    __slots__ = "value"
    def __init__(self):
        self.value = True

    def invalidate(self):
        print("hey")
        self.value = False

    def __bool__(self):
        return self.value

Request = collections.namedtuple("RequestTuple",["block","priority","valid_tag","callback","exclusive"])

blockread_counter = 0
class World(voxelengine.World):
    BlockClass = resources.Block
    PlayerEntityClass = resources.entityClasses["Character"]
    def __init__(self,*args,**kwargs):
        super(World,self).__init__(*args,**kwargs)
        self.changed_blocks = []
        self.set_requests = collections.defaultdict(list) # position: [Request,...]
        self.move_requests = [] # (position_from, position_to)
        
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
        ui.set_stats("changed_blocks",len(self.changed_blocks))
        # do entity updates
        if self.changed_blocks:
            for entity in self.get_entities(): #M# limited distance, not all?
                entity.block_update()

        # do timestep for blockupdates -> first compute all then update all, so update order doesn't matter
        resources.Block.defer = True
        block_updates = [(position-face, face) for position in self.changed_blocks
                                               for face in ((-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1),(0,0,0))]
        self.changed_blocks = []
        block_updates.sort(key = lambda x:x[0]) # necessary for groupby to work
        for position, group in itertools.groupby(block_updates,lambda x:x[0]):
            faces = [x[1] for x in group]
            self[position].block_update(faces)
        resources.Block.defer = False
        while resources.Block.deferred:
            block, key, value = resources.Block.deferred.pop()
            block[key] = value

        # translate move_requests
        for position_from, position_to in self.move_requests:
            valid_tag = ValidTag()
            block = self.get_block(position_from)
            self.set_requests[position_from].append(Request("AIR",0,valid_tag,None,True))
            self.set_requests[position_to  ].append(Request(block,0,valid_tag,None,True))
        self.move_requests = []

        # handle set_requests
        for requests in self.set_requests.values():
            max_priority = max(request.priority for request in requests)
            dominant_requests = []
            for request in requests:
                if request.priority == max_priority:
                    dominant_requests.append(request)
                else:
                    request.valid_tag.invalidate()
            if len(dominant_requests) > 1:
                for request in dominant_requests:
                    if request.exclusive:
                        request.valid_tag.invalidate()
        
        for position, requests in  self.set_requests.iteritems():
            for request in requests:
                if request.valid_tag:
                    self.set_block(position, request.block)
                if request.callback:
                    request.callback(request.valid_tag)
        self.set_requests.clear()
    
    def request_move_block(self, position_from, position_to):
        self.move_requests.append((position_from, position_to))

    def request_set_block(self, position, blockname, priority, valid_tag, callback, exclusive):
        pass

class UI(object):
    def __init__(self, config, worldtypes):
        config["worldtype"] = select(worldtypes)[1]
        config["run"] = True
    def set_stats(self, name, value):
        print(name, value)

def zeitmessung(ts = [0]*200, t = [time.time()]):
    dt = time.time() - t[0]
    t[0] += dt
    dt = round(1/dt,2)
    ts.append(dt)
    ts.pop(0)
    ui.set_stats("dt",dt)
    ui.set_stats("min dt", min(ts))
    ui.set_stats("max dt", max(ts))

def gameloop():
    global w, g
    while not config["quit"]:
        #wait for config being ready to start
        if not config["run"]:
            time.sleep(0.1)
            continue #jump back to start of loop
        print("Game starting ...", end="")
        worldmod = imp.load_source(config["worldtype"],os.path.join(PATH,"resources","Welten",config["worldtype"])+".py")

        w = World(worldmod.terrain_generator,spawnpoint=worldmod.spawnpoint,chunksize=CHUNKSIZE,defaultblock=resources.Block("AIR"),filename=config["file"])
        if len(w.chunks) == 0: # only generate if not done yet
            worldmod.init(w)
        w.changed_blocks = []

        def save():
            print("Game saving ...", end="")
            if config["file"]:
                w.save(config["file"])
                print("done")
            else:
                print("skipped")
            config["save"] = False

        def i_f(player):
            w.spawn_player(player)
            player.init()

        renderlimit = True #True: fast loading, False: whole world at once
        settings = {"init_function": i_f,
                    "renderlimit": True,#renderlimit, # whether to show just the chunks in renderdistance (True) or all loaded chunks (False)
                    "suggested_texturepack" : os.path.join("..","..","..","resources","texturepack"),
                    "PlayerClass" : Player,
                    "wait" : False,
                    "name" : config["name"],
                    }
        t = time.time()
        FPS = 60
        with voxelengine.Game(**settings) as g:
            print("done") # Game starting ... done
            while config["run"]:
                if config["play"]:
                    config["play"] = False
                    g.launch_client()
                if config["save"]:
                    save()
                dt = time.time() - t
                time.sleep(max(0, 1.0/FPS-dt))
                t = time.time()
                ui.set_stats("bla", "%s, %s" %(1.0/FPS, dt))
                ui.set_stats("sleep", max(0, 1.0/FPS-dt))
                zeitmessung()
                #print blockread_counter
                blockread_counter = 0
                #
                g.update()
                w.tick()
                for player in g.get_players():
                    player.update()
                    player.do_random_ticks()
                #M#
                if config["mobspawning"]:
                    for entity_class in resources.entityClasses.values():
                        if len(entity_class.instances) < entity_class.LIMIT:
                            entity_class.try_to_spawn(w)
                for entity in w.entities.copy():
                    entity.update()
            save()
        print("Game stopped")
    rememberconfig = config.copy()
    for key in ("run","play","quit","save"):
        rememberconfig.pop(key)
    with open(configfn,"w") as configfile:
        configfile.write(repr(rememberconfig))
    print()
    print("Bye!")
    time.sleep(1)
    
config = {  "name"       : "%ss MCGCraft Server" %getpass.getuser(),
            "file"       : "",
            "worldtype"  : "Colorland",
            "mobspawning": True,
            "whitelist"  : "127.0.0.1",
            "parole"     : "",
            "port"       : "",
            "run"        : False,
            "play"       : False,
            "quit"       : False,
            "save"       : False,
         }

configdir = appdirs.user_config_dir("MCGCraft","ProgrammierAG")
print(configdir)
configfn = os.path.join(configdir,"serversettings.py")
def main():
    global ui
    if os.path.exists(configfn):
        with open(configfn,"r") as configfile:
            rememberedconfig = ast.literal_eval(configfile.read())
        config.update(rememberedconfig)
    elif not os.path.exists(configdir):
        os.makedirs(configdir)
        
    worldtypes = os.listdir(os.path.join("resources","Welten"))
    worldtypes = [x[:-3] for x in worldtypes if x.endswith(".py") and not x.startswith("_")]
    try:
        from gui.tkgui import GUI as UI
    except ImportError as e:
        print("GUI not working cause of:\n",e)
    ui = UI(config, worldtypes)

    if sys.flags.interactive or False:
        thread.start_new_thread(gameloop,())
        if not sys.flags.interactive:
            import code
            code.interact(local=locals())
    else:
        gameloop()
        
if __name__ == "__main__":
    main()
