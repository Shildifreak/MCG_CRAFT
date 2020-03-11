#! /usr/bin/env python3
#* encoding: utf-8 *#

#if __name__ != "__main__":
#    raise Warning("mcgcraft.py should not be imported")

# Imports
import sys, os, ast, imp, inspect
import _thread as thread
import math, time, random, itertools, collections
import getpass
import copy
import pprint

PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(os.path.join(PATH,"lib"))
sys.path.append(os.path.join(PATH,"resources","Welten","structures"))

import resources
import voxelengine
import voxelengine.modules.appdirs as appdirs
import voxelengine.modules.utils

from voxelengine.modules.shared import *
from voxelengine.modules.geometry import Vector, EVERYWHERE, Sphere
import voxelengine.server.world_data_template

class InventoryDisplay():
    def __init__(self,player):
        self.player = player
        self.is_open = False #Full inventory or only hotbar
        self.inventory = None
        self.foreign_inventory = None
        self.current_pages = [0,0]

    def register(self, inventory):
        self.unregister()
        self.inventory = inventory
        if self.inventory:
            self.inventory.register_callback(self.callback)                
    def unregister(self):
        if self.inventory:
            self.inventory.unregister_callback(self.callback)                        

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
        #hier prüfen ob x in inventory rein darf
        if not inventory.may_contain(x):
            return
        #
        x.parent = None
        y.parent = None
        self.player.entity[hand], inventory[index] = y, x    




class Player(voxelengine.Player):
    RENDERDISTANCE = 10

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.set_focus_distance(8)
        self.flying = False
        self.inventory_display = InventoryDisplay(self)

    def create_character(self):
        world = self.universe.get_spawn_world()
        character = resources.entityClasses["Mensch"]()
        character.set_world(world,world.blocks.world_generator.spawnpoint)

        # just for testing:
        character["inventory"] = [{"id":"RACKETENWERFER"},{"id":"DOORSTEP","count":1},{"id":"Repeater"},{"id":"FAN"},{"id":"Setzling"},{"id":"HEBEL"},{"id":"WAND"},{"id":"BARRIER"},{"id":"LAMP"},{"id":"TORCH"},{"id":"Redstone","count":128},{"id":"CHEST"},{"id":"Kredidtkarte"}]
        for blockname in resources.blockClasses.keys():
            character["inventory"].append({"id":blockname})
        character["left_hand"] = {"id":"STONE","count":100}
        character["right_hand"] = {"id":"SAND","count":100}

        # inventory stuff
        for i in range(60):
            character["inventory"].append({"id":"AIR","count":i})
        return character

    def control(self, entity):
        if self.entity:
            self.entity.unregister_item_callback(self._open_inventory_callback,"open_inventory")
            self.entity.unregister_item_callback(self._update_left_hand_image,"left_hand")
            self.entity.unregister_item_callback(self._update_right_hand_image,"right_hand")
            self.entity.unregister_item_callback(self._update_lives,"lives")
        super().control(entity)
        if self.entity:
            self.inventory_display.register(self.entity["inventory"])
            self.entity.register_item_callback(self._open_inventory_callback,"open_inventory")
            self.entity.register_item_callback(self._update_left_hand_image,"left_hand")
            self.entity.register_item_callback(self._update_right_hand_image,"right_hand")
            self.entity.register_item_callback(self._update_lives,"lives")

    def _open_inventory_callback(self, boolean):
        if boolean:
            self.inventory_display.open(self.entity.foreign_inventory)
            self.entity.foreign_inventory = None
        else:
            self.inventory_display.close()
    def _update_left_hand_image(self, item):
        self.display_item("left_hand",item,(-0.8,-0.8,0.5),(0.1,0.1),BOTTOM|LEFT)
    def _update_right_hand_image(self, item):
        self.display_item("right_hand",item,(0.8,-0.8,0.5),(0.1,0.1),BOTTOM|RIGHT)
    def _update_lives(self, lives):
        #todo: fix!
        for x in range(lives,10):
            self.del_hud("heart"+str(x))
        for x in range(lives):
            self.set_hud("heart"+str(x),"HERZ",Vector((-0.97+x/10.0,0.95,0)),0,(0.05,0.05),INNER|CENTER)

    def update(self):
        # stuff that doesn't need entity
        if self.was_pressed("fly"):
            self.flying = not self.flying
        if self.was_pressed("inv"):
            self.inventory_display.toggle()
        for pressed in self.was_pressed_set:
            if pressed.startswith("left clicked inventory") or pressed.startswith("right clicked inventory"):
                self.inventory_display.handle_click(pressed)

        # stuff that needs entity
        if not self.entity:
            return
        pe = self.entity
        #if not self.is_active(): # freeze player if client doesnt respond
        #    return

        #           left click      right click
        # no shift  mine block      activate block
        # shift     use l item      use r. item
                
        get_block = lambda: pe.world.blocks[pos]
        def get_item():
            hand_name = {"left click": "left_hand", "right click":"right_hand"}[event_name]
            item_data = pe[hand_name]
            return resources.itemClasses[item_data["id"]](item_data)

        for event_name in ("left click", "right click"):
            if self.was_pressed(event_name):
                d_block, pos, face = self.entity.get_focused_pos(self.focus_distance)
                d_entity, entity = self.entity.get_focused_entity(self.focus_distance)

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

        speed_modifier = 5 if self.is_pressed("sprint") else 1

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
            if nv != (0,0,0):
                pe["position"] += nv*pe["FLYSPEED"]*speed_modifier*pe.dt
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
        if l > pe["SPEED"]*speed_modifier:
            f = pe["SPEED"]*speed_modifier / l
            pe["velocity"] *= (f,1,f)

        # save previous velocity and onground
        vy_vorher = pe["velocity"][1]
        onground_vorher = pe.onground()
        position_vorher = pe["position"]
        # update position
        pe.update_position()
        # see if player hit the ground and calculate damage
        onground_nachher = pe.onground()
        if (not onground_vorher) and onground_nachher:
            # Geschwindigkeit 20 entspricht etwa einer Fallhoehe von 6 Block, also ab 7 nimmt der Spieler Schaden
            schaden = (-vy_vorher) -20
            # HERZEN ANPASSEN
            if schaden >0:
                a = pe["lives"]
                b = pe["lives"] - 1

                pe["lives"] = b
        # reset position when shifting and leaving ground
        if self.is_pressed("shift") and onground_vorher and not onground_nachher:
            pe["position"] = position_vorher
            pe["velocity"] = Vector(0,0,0)

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
        print("mcgcraft.py ValidTag.invalidate was called")
        self.value = False

    def __bool__(self):
        return self.value

Request = collections.namedtuple("RequestTuple",["block","priority","valid_tag","callback","exclusive"])

#blockread_counter = 0
class World(voxelengine.World):
    def __init__(self,*args,**kwargs):
        super(World,self).__init__(*args,**kwargs)
        self.blocks.BlockClass = resources.Block
        
        self.changed_blocks = []
        self.set_requests = collections.defaultdict(list) # position: [Request,...]
        self.move_requests = [] # (position_from, position_to)
        
    #def get_block(self,position,*args,**kwargs):
    #    global blockread_counter
    #    blockread_counter += 1
    #    return super(World,self).get_block(position,*args,**kwargs)

    def tick(self):
        super(World,self).tick()
        self.handle_block_requests()

    def random_ticks_at(self, position):
        radius = 2 #M# increase later but for now this would cause too much lag
        rate = 0.5
        tickable_blocks = self.blocks.find_blocks(Sphere(position, radius), "random_tick")
        for block in tickable_blocks:
            if random.random() < rate:
                block.handle_event_random_tick()

    def handle_block_requests(self):
        # translate move_requests
        for position_from, position_to in self.move_requests:
            valid_tag = ValidTag()
            block = self.blocks[position_from]
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
        
        for position, requests in  self.set_requests.items():
            for request in requests:
                if request.valid_tag:
                    self.blocks[position] = request.block
                if request.callback:
                    request.callback(request.valid_tag)
        self.set_requests.clear()
    
    def request_move_block(self, position_from, position_to):
        self.move_requests.append((position_from, position_to))

    def request_set_block(self, position, blockname, priority, valid_tag, callback, exclusive):
        self.set_requests[position].append(Request(blockname, priority, valid_tag, callback, exclusive))

class UI(object):
    def __init__(self, config, worldtypes):
        config["worldtype"] = select(worldtypes)[1]
        config["run"] = True
    def set_stats(self, name, value):
        print(name, value)

class Timer(object):
    def __init__(self, TPS):
        self.TPS = TPS # desired TPS
        self.t = time.time() # timestamp of last tick
        self.dt = None # length of last tick
        self.dt_work = None
        self.dt_idle = None
    def tick(self):
        self.dt_work = time.time() - self.t #time since last tick
        self.dt_idle = max(0, 1.0/self.TPS - self.dt_work)
        time.sleep(self.dt_idle)
        self.dt = time.time() - self.t
        self.t += self.dt

def zeitstats(timer, tps_history = [0]*200):
    tps = round(1/timer.dt,2)
    tps_history.append(tps)
    tps_history.pop(0)
    ui.set_stats("TPS",tps)
    ui.set_stats("min TPS", min(tps_history))
    ui.set_stats("max TPS", max(tps_history))
    
    ui.set_stats("mspt", "%s / %s" %(int(1000*timer.dt_work), int(1000/timer.TPS)))
    ui.set_stats("sleep", int(1000*timer.dt_idle))

def gameloop():
    global w, g
    while not config["quit"]:
        #wait for config being ready to start
        if not config["run"]:
            time.sleep(0.1)
            continue #jump back to start of loop

        savegamepath = config["file"]
        if os.path.exists(savegamepath):
            print("Loading World ...", end="")
            with open(savegamepath) as savegamefile:
                data = World.parse_data_from_string(savegamefile.read())
            w = World(data)
            print("done")
        else:
            print("Preparing World ...", end="")
            data = copy.deepcopy(voxelengine.server.world_data_template.data)
            generator_data = data["block_world"]["generator"]
            generator_data["name"] = config["worldtype"]
            generator_data["seed"] = random.random()
            generator_data["path"] = os.path.join(PATH,"resources","Welten",config["worldtype"])
            generator_data["path_py"] = generator_data["path"] + ".py"
            generator_data["path_js"] = generator_data["path"] + ".js"
            if os.path.isfile(generator_data["path_py"]):
                with open(generator_data["path_py"]) as generator_file_py:
                    generator_data["code_py"] = generator_file_py.read()
            else:
                    generator_data["code_py"] = ""
            if os.path.isfile(generator_data["path_js"]):
                with open(generator_data["path_js"]) as generator_file_js:
                    generator_data["code_js"] = generator_file_js.read()
            else:
                    generator_data["code_js"] = ""
            print("done")
            print("Creating World ... ", end="", flush=True)
            w = World(data)
            print("done")
            print("Initialising world ... ", end="", flush=True)
            t = time.time()
            w.blocks.world_generator.init(w)
            w.event_system.clear_events()
            dt = time.time() - t
            print("done")
            print("(", len(w.blocks.block_storage.structures), "blocks in", dt, "s )")

        def save():
            print("Preparing Savestate ... ", end="", flush=True)
            data = w.serialize()
            data_string = repr(data)
            print("done")
            print("Checking Savestate ... ", end="", flush=True)
            try:
                World.parse_data_from_string(data_string)
            except Exception as e:
                print("failed: world data not parsable")
                pprint.pprint(data)
                print(e)
            else:
                print("passed")
                print("Game saving ... ", end="", flush=True)
                if config["file"]:
                    with open(config["file"], "w") as savegamefile:
                        savegamefile.write(data_string)
                    print("done")
                else:
                    print("skipped: missing path")
            config["save"] = False

        u = voxelengine.Universe()
        u.worlds.append(w)

        settings = {"wait" : False,
                    "name" : config["name"],
                    "parole" : config["parole"],
                    "texturepack_path" : os.path.join(PATH,"resources","texturepacks",config["texturepack"],".versions"),
                    "PlayerClass" : Player,
                    }
        timer = Timer(TPS = 60)
        print("Server starting ...", end="")
        with voxelengine.GameServer(u, **settings) as g:
            ui.set_stats("ip",voxelengine.modules.utils.get_ip())
            ui.set_stats("discovery_port",g.socket_server.port)
            ui.set_stats("game_port",g.socket_server.entry_port)
            ui.set_stats("http_port",g.http_port)
            print("done") # Server starting ... done
        
            while config["run"]:
                if config["play"]:
                    config["play"] = False
                    g.launch_client(config["clienttype"], config["username"], config["password"])
                if config["save"]:
                    save()
                timer.tick()
                zeitstats(timer)
                
                # game update
                g.update()

                ui.set_stats("events",sum(map(len, w.event_system.event_queue)))

                # tick worlds (only the ones with players in them?)
                u.tick()
                
                # player update
                for player in g.get_players():
                    player.update()


                # random ticks
                for random_tick_source in w.entities.find_entities(EVERYWHERE, "random_tick_source"):
                    w.random_ticks_at(random_tick_source["position"])

                #M# mob spawning
                if config["mobspawning"]:
                    for entity_class in resources.entityClasses.values():
                        if len(entity_class.instances) < entity_class.LIMIT:
                            entity_class.try_to_spawn(w)
 
                # entity update
                for entity in tuple(w.entities.find_entities(EVERYWHERE, "update")): #M# replace with near player(s) sometime, find a way to avoid need for making copy
                    entity.update()
                
                # Stats
                blockread_counter = 0
                #ui.set_stats("block reads", blockread_counter)
                
            save()
        print("Game stopped")
    save_config()
    print()
    print("Bye!")
    time.sleep(1)
    
config = {  "name"       : "%ss MCGCraft Server" %getpass.getuser(),
            "file"       : "",
            "worldtype"  : "Colorland",
            "mobspawning": True,
            "whitelist"  : "127.0.0.1",
            "parole"     : "",
            "username" : "",
            "password" : "",
            "clienttype" : "desktop",
            "texturepack": "default",
            "port"       : "",
            "run"        : False,
            "play"       : False,
            "quit"       : False,
            "save"       : False,
            
            "auto_create_entities_for_players":True,
         }

configdir = appdirs.user_config_dir("MCGCraft","ProgrammierAG")
configfn = os.path.join(configdir,"serversettings.py")
print(configfn)

def load_config():
    if os.path.exists(configfn):
        with open(configfn,"r") as configfile:
            rememberedconfig = ast.literal_eval(configfile.read())
        config.update(rememberedconfig)
    elif not os.path.exists(configdir):
        os.makedirs(configdir)

def save_config():
    rememberconfig = config.copy()
    for key in ("run","play","quit","save","refresh","address"):
        rememberconfig.pop(key, None)
    with open(configfn,"w") as configfile:
        configfile.write(repr(rememberconfig))

def main():
    global ui
    load_config()
    worldtypes = os.listdir(os.path.join(PATH,"resources","Welten"))
    worldtypes = sorted(set([x[:-3] for x in worldtypes if (x.endswith(".py") or x.endswith(".js")) and not x.startswith("_")]))
    clienttypes = os.listdir(os.path.join(PATH,"lib","voxelengine","client"))
    try:
        from gui.tkgui import ServerGUI as UI
    except ImportError as e:
        print("GUI not working cause of:\n",e)
    ui = UI(config, worldtypes, clienttypes)

    if False: #M# sys.flags.interactive or False:
        thread.start_new_thread(gameloop,())
        if not sys.flags.interactive:
            import code
            code.interact(local=locals())
    else:
        gameloop()
        
if __name__ == "__main__":
    main()
