#! /usr/bin/env python3
#* encoding: utf-8 *#

#if __name__ != "__main__":
#    raise Warning("mcgcraft.py should not be imported")

# Imports
import sys, os, ast, imp, inspect, select
import threading, _thread, signal
import math, time, random, itertools, collections
import getpass
import copy
import pprint
import json
import argparse
import socket

PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(os.path.join(PATH,"lib"))
sys.path.append(os.path.join(PATH,"resources","Welten","structures"))

import resources
import voxelengine

from gui.config import Config, default_serverconfig
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
            if k == 0:
                self.player.entity[hand] = self._calculate_index(k,row,col)
        else:
            k, direction = map(int,args)
            inventory = self.inventory if k==0 else self.foreign_inventory
            self.current_pages[k] = max(0,self.current_pages[k] + direction)
            self.display()
    
    def handle_drag(self,event):
        button, dragged, from_element, to_element = event.split(" ")
        if from_element.startswith("inventory") and to_element.startswith("inventory"):
            from_args = from_element.rsplit("(",1)[1].split(")",1)[0].split(",")
            to_args = to_element.rsplit("(",1)[1].split(")",1)[0].split(",")
            if len(from_args) == 3 and len(to_args) == 3:
                from_k, from_col, from_row = map(int, from_args)
                to_k, to_col, to_row = map(int, to_args)
                from_inventory = self.inventory if from_k==0 else self.foreign_inventory
                to_inventory = self.inventory if to_k==0 else self.foreign_inventory
                from_index = self._calculate_index(from_k, from_row, from_col)
                to_index = self._calculate_index(to_k, to_row, to_col)
                if False: #check if they could stack
                    pass #add them together
                else: #swap
                    self.swap(from_inventory, from_index, to_inventory, to_index)
    
    def swap(self,inventory1,index1,inventory2,index2):
        # prüfen ob die Items in das jeweils andere Inventar hineindürfen
        if (not inventory1.may_contain(inventory2[index2])) or \
           (not inventory2.may_contain(inventory1[index1])):
            return
        # prüfen dass die items nicht dasselbe sind, weil sonst das Vertauschen das Item löscht
        if inventory1 == inventory2 and index1 == index2:
            return
        # ersetzen mit AIR um den index in der Liste nicht zu verändern (wichtig falls zwei Dinge aus dem selben inventar getauscht werden sollen)
        x = inventory1.replace(index1, {"id":"AIR"})
        y = inventory2.replace(index2, x)
        inventory1.replace(index1, y)

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
        character["inventory"] = [{"id":"STONE","count":100},{"id":"SAND","count":100},{"id":"RACKETENWERFER"},{"id":"DOORSTEP","count":1},{"id":"Repeater"},{"id":"FAN"},{"id":"Setzling"},{"id":"HEBEL"},{"id":"WAND"},{"id":"BARRIER"},{"id":"LAMP"},{"id":"TORCH"},{"id":"Redstone","count":128},{"id":"CHEST"},{"id":"Kredidtkarte"},{"id":"TESTBLOCK"},{"id":"GESICHT"}]
        for blockname in resources.blockClasses.keys():
            character["inventory"].append({"id":blockname})
        character["left_hand"] = 0
        character["right_hand"] = 16

        # inventory stuff
        for i in range(60):
            character["inventory"].append({"id":"AIR","count":i})
        return character

    def control(self, entity):
        if self.entity:
            self.entity.unregister_item_callback(self._open_inventory_callback,"open_inventory")
            self.entity.unregister_item_callback(self._update_left_hand_image,"left_hand")
            self.entity.unregister_item_callback(self._update_left_hand_image,"inventory")
            self.entity.unregister_item_callback(self._update_right_hand_image,"right_hand")
            self.entity.unregister_item_callback(self._update_right_hand_image,"inventory")
            self.entity.unregister_item_callback(self._update_lives,"lives")
        super().control(entity)
        if self.entity:
            self.inventory_display.register(self.entity["inventory"])
            self.entity.register_item_callback(self._open_inventory_callback,"open_inventory")
            self.entity.register_item_callback(self._update_left_hand_image,"left_hand")
            self.entity.register_item_callback(self._update_left_hand_image,"inventory")
            self.entity.register_item_callback(self._update_right_hand_image,"right_hand")
            self.entity.register_item_callback(self._update_right_hand_image,"inventory")
            self.entity.register_item_callback(self._update_lives,"lives")

    def _open_inventory_callback(self, boolean):
        if boolean:
            self.inventory_display.open(self.entity.foreign_inventory)
            self.entity.foreign_inventory = None
        else:
            self.inventory_display.close()
    def _update_left_hand_image(self, _):
        item = self.entity["inventory"][self.entity["left_hand"]]
        self.display_item("left_hand",item,(-0.8,-0.8,0.5),(0.1,0.1),BOTTOM|LEFT)
    def _update_right_hand_image(self, _):
        item = self.entity["inventory"][self.entity["right_hand"]]
        self.display_item("right_hand",item,(0.8,-0.8,0.5),(0.1,0.1),BOTTOM|RIGHT)
    def _update_lives(self, lives):
        #todo: fix!
        for x in range(lives,10):
            self.del_hud("heart"+str(x))
        for x in range(lives):
            self.set_hud("heart"+str(x),"HERZ",Vector((-0.97+x/10.0,0.95,0)),0,(0.05,0.05),INNER|CENTER)

    def update(self):
        if not self.entity:
            return
        pe = self.entity

        if self.was_pressed("fly"):
            self.flying = not self.flying
        if self.was_pressed("inv"):
            self.inventory_display.toggle()
        for pressed in self.was_pressed_set:
            if pressed.startswith("left clicked inventory") or pressed.startswith("right clicked inventory"):
                self.inventory_display.handle_click(pressed)
            if pressed.startswith("left dragged inventory") or pressed.startswith("right dragged inventory"):
                self.inventory_display.handle_drag(pressed)
            if pressed.startswith("inv") and pressed != "inv":
                inv_slot = int(pressed[3:])
                hand = "left_hand" if self.is_pressed("shift") else "right_hand"
                pe[hand] = inv_slot
            if pressed.startswith("scrolling"):
                inv_inc_float = -float(pressed[10:])
                hand = "left_hand" if self.is_pressed("shift") else "right_hand"
                threshold = 0.1
                inv_inc = (inv_inc_float >= threshold) - (inv_inc_float <= -threshold) #sign with -1,0,1 and threshold for 0
                inv_slot = pe[hand] + inv_inc
                inv_slot %= 7
                pe[hand] = inv_slot
                

        #if not self.is_active(): # freeze player if client doesnt respond
        #    return

        #           left click      right click
        # no shift  mine block      activate block
        # shift     use l item      use r. item
                
        get_block = lambda: pe.world.blocks[pos]
        def get_item():
            hand_name = {"left_hand": "left_hand", "right_hand":"right_hand"}[event_name]
            item_index = pe[hand_name]
            item_data = pe["inventory"][item_index]
            return resources.itemClasses[item_data["id"]](item_data)

        for event_name in ("left_hand", "right_hand"):
            if self.was_pressed(event_name):
                d_block, pos, face = self.entity.get_focused_pos(self.focus_distance)
                d_entity, entity = self.entity.get_focused_entity(self.focus_distance)

                # nothing to click on
                if (d_block == None) and (d_entity == None):
                    get_item().use_on_air(pe)
                    continue

                # click on block
                if (d_block != None) and ((d_entity == None) or (d_block < d_entity)):
                    actions = {"right_hand": (lambda:get_block().activated(pe, face),
                                              lambda:get_item().use_on_block(pe, pos, face)),
                               "left_hand" : (lambda:get_block().mined(pe, face),
                                              lambda:get_item().use_on_block(pe, pos, face))
                               }[event_name]
                # click on entity
                else:
                    actions = {"right_hand": (lambda:get_item().use_on_entity(pe, entity),
                                              lambda:entity.right_clicked(pe)),
                               "left_hand" : (lambda:get_item().use_on_entity(pe, entity),
                                              lambda:entity.left_clicked(pe))}[event_name]
                action1, action2 = actions
                if self.is_pressed("shift"): #if shift is pressed skip action1 and definitely do action2
                    do_next = True
                else:
                    do_next = action1()
                #if action1 didn't really do anything automatically switch to action2, eg. if activating doesn't work just place a block
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
    __slots__ = ("value", "callback")
    def __init__(self, callback=None):
        self.value = True
        self.callback = callback

    def invalidate(self):
        print("mcgcraft.py ValidTag.invalidate was called")
        self.value = False

    def __bool__(self):
        return self.value

Request = collections.namedtuple("RequestTuple",["block","priority","valid_tag","exclusive"])

#blockread_counter = 0
class World(voxelengine.World):
    def __init__(self,*args,**kwargs):
        super(World,self).__init__(*args,**kwargs)
        self.blocks.BlockClass = resources.Block
        
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
        for position_from, position_to, callback in self.move_requests:
            valid_tag = ValidTag(callback)
            block = self.blocks[position_from]
            self.set_requests[position_from].append(Request("AIR",0,valid_tag,True))
            self.set_requests[position_to  ].append(Request(block,0,valid_tag,True))
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
        
        valid_tags = set()
        for position, requests in self.set_requests.items():
            for request in requests:
                if request.valid_tag:
                    self.blocks[position] = request.block
                valid_tags.add(request.valid_tag)
        for valid_tag in valid_tags:
            if valid_tag.callback:
                valid_tag.callback(bool(valid_tag))
        self.set_requests.clear()
    
    def request_move_block(self, position_from, position_to, callback=None):
        self.move_requests.append((position_from, position_to, callback))

    def request_set_block(self, position, blockname, priority, valid_tag, exclusive):
        self.set_requests[position].append(Request(blockname, priority, valid_tag, exclusive))

class Timer(object):
    def __init__(self):
        self.t = time.time() # timestamp of last tick
        self.dt = None # length of last tick
        self.dt_work = None
        self.dt_idle = None
    def tick(self, TPS):
        mspt = 1.0/TPS
        self.dt_work = time.time() - self.t #time since last tick
        self.dt_idle = max(0, mspt - self.dt_work)
        time.sleep(self.dt_idle)
        self.dt = time.time() - self.t
        self.t += self.dt

def zeitstats(timer, tps_history = [0]*200):
    tps = round(1/timer.dt,2)
    tps_history.append(tps)
    tps_history.pop(0)
    stats.set("TPS",tps)
    stats.set("min TPS", min(tps_history))
    stats.set("max TPS", max(tps_history))
    
    stats.set("mspt", int(round(1000*timer.dt_idle+1000*timer.dt_work)))
    stats.set("work",  int(1000*timer.dt_work))
    stats.set("sleep", int(1000*timer.dt_idle))

def run():
    global w, g
    savegamepath = config["file"]
    if os.path.exists(savegamepath):
        print("== Loading World ==")
        with open(savegamepath) as savegamefile:
            data = World.parse_data_from_string(savegamefile.read())
        w = World(data)
    else:
        print("== Preparing World ==")
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
        print("== Creating World ==", flush=True)
        w = World(data)
        print("== Initialising world ==", flush=True)
        t = time.time()
        w.blocks.world_generator.init(w)
        w.event_system.clear_events()
        dt = time.time() - t
        print("(", len(w.blocks.block_storage.structures), "blocks in", dt, "s )")

    def save():
        print("Preparing Savestate", flush=True)
        data = w.serialize()
        data_string = repr(data)
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
                "host" : config["host"],
                "http_port" : config["http_port"],
                }
    timer = Timer()
    print("== Server starting ==")
    with voxelengine.GameServer(u, **settings) as g:
        stats.set("host",g.host)
        stats.set("discovery_port",g.info_server.port)
        stats.set("game_port",g.game_port)
        stats.set("http_port",g.http_port)
        print("== Server running ==") # Server starting ... done
    
        quitFlag = False
        while not quitFlag:
            # handle commands from stdin
            for command in get_inputs():
                if command == "quit":
                    quitFlag = True
                elif command == "save":
                    save()
                elif command == "reload":
                    load_config()
                elif command == "stats":
                    print(stats)
                elif command.startswith("play"):
                    play,*args = command.split(" ")
                    if 1 <= len(args) <= 3:
                        g.launch_client(*args)
                    else:
                        print("use like this: play clienttype [username] [password]")
                else:
                    print("valid commands include: quit, save, reload, stats")
            
            # game server update - communicate with clients
            g.update()

            # to idle or not to idle
            TPS = config["tps"] if g.get_players() else config["idle_tps"]
            if TPS == 0:
                time.sleep(1)
                continue

            # player update
            for player in g.get_players():
                player.update()

            #M# mob spawning
            if config["mobspawning"]:
                for entity_class in resources.entityClasses.values():
                    if len(entity_class.instances) < entity_class.LIMIT:
                        entity_class.try_to_spawn(w)

            # entity update
            for entity in tuple(w.entities.find_entities(EVERYWHERE, "update")): #M# replace with near player(s) sometime, find a way to avoid need for making copy
                entity.update()

            # random ticks
            for random_tick_source in w.entities.find_entities(EVERYWHERE, "random_tick_source"):
                w.random_ticks_at(random_tick_source["position"])

            # tick worlds (only the ones with players in them?)
            stats.set("events",sum(map(len, w.event_system.event_queue)))
            u.tick()
            
            # Stats
            timer.tick(TPS)
            zeitstats(timer)
            blockread_counter = 0
            #stats.set("block reads", blockread_counter)
            
        save()
    print("Game stopped")
    time.sleep(1)
    print("Bye!")

def load_config():
    global config
    config = Config(args.configfile, default_serverconfig)
    for key in config:
        value = getattr(args,key,None)
        if value:
            if not isinstance(config[key], str):
                value = ast.literal_eval(value)
            config[key] = value

def parse_args():
    global args
    parser = argparse.ArgumentParser(description="This is a voxelengine client")
    parser.add_argument("configfile",
                  help="path to a server config file", metavar="CONFIGFILE",
                  nargs='?', #make configfile optional
                  action="store")
    parser.add_argument("--stats-port", dest="stats_port",
                  help="send server status updates to this port on localhost",type=int,
                  action="store")
    for key in default_serverconfig:
        parser.add_argument("--"+key, dest=key, help="defaults to %s"%repr(default_serverconfig[key]))
    args = parser.parse_args()

class StatsHandler(object):
    def __init__(self):
        self.stats = {}
        self.sinks = []
    def __str__(self):
        ls = tuple(len("%s: %s"%item) for item in self.stats.items())
        maxl = min(80, max(ls))
        template = lambda l:"%s: "+" "*(maxl-l)+"%s"
        return "\n".join(template(l)%item for (l, item) in zip(ls, self.stats.items()))
    def set(self, name, value):
        self.stats[name] = value
        data = json.dumps((name, value))
        for sink in self.sinks:
            sink(data)
    def add_sink(self, sink):
        self.sinks.append(sink)
    def add_socket_sink(self, address):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect(address)
        self.sinks.append(lambda msg: self.socket.send(msg.encode()+b"\n"))
    def add_file_sink(self, f):
        self.add_sink(lambda msg:f.write(msg))

stats = StatsHandler()
#stats.add_file_sink(sys.stdout)

def get_inputs():
    while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline()
        if line:
            yield line.rstrip()
        else: # an empty line means EOF
            yield "quit"
            return

def main():
    parse_args()
    if args.stats_port:
        stats.add_socket_sink(("localhost",args.stats_port))
    load_config()
    run()

if __name__ == "__main__":
    main()



#usage: mcgcraft-server --send-stats-to localhost:56789 
