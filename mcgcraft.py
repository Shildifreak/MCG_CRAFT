#! /usr/bin/env python3
#* encoding: utf-8 *#

# Imports
import sys, os, ast, inspect, select
import threading
import time, random, collections
import queue
import copy
import pprint
import json
import argparse
import socket

PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(os.path.join(PATH,"lib"))

import resources
import voxelengine

from config import Config, default_serverconfig
from voxelengine.modules.shared import *
from voxelengine.modules.geometry import Vector, EVERYWHERE, SOMEWHERE, Sphere, Point
from voxelengine.modules.observableCollections import ObservableList, ObservableDict, observable_from
from voxelengine.server.event_system import Event
import voxelengine.server.world_data_template

class InventoryWrapper(object):
    """subclasses are designed to unifiy access to entity and block inventories"""

    def __init__(self):
        self.open = 0

    def __enter__(self, *args):
        self.open += 1

    def __exit__(self, *args):
        assert self.open
        self.open -= 1

    def __getitem__(self, key):
        assert self.open
        return self.inventory[key]

    def get(self, index, default_value):
        assert self.open
        return self.inventory.get(index, default_value)
    
    def replace(self, index, value):
        assert self.open
        return self.inventory.replace(index, value)
    
    def may_contain(self, item):
        assert self.open
        return self.inventory.may_contain(item)

    def on_close(self): #this on close is not directly related to the open attribute above
        assert self.open
        if hasattr(self.inventory, "on_close"):
            self.inventory.on_close()

class BlockInventoryWrapper(InventoryWrapper):
    def __init__(self, world, position):
        super().__init__()
        self.world = world
        self.position = position
        self.observers = dict()
    
    def __eq__(self, other):
        if not isinstance(other, BlockInventoryWrapper):
            return False
        if self.world is other.world and self.position == other.position:
            return True
        return False

    def __enter__(self, *args):
        # open if not open already
        if not self.open:
            self.changed = False
            self.block = self.world.blocks[self.position]
            self.inventory = observable_from(dict(self.block["inventory"]))
        # increment open counter
        self.open += 1
        
    def __exit__(self, *args):
        # make sure it was open before
        assert self.open
        # decrement open counter
        self.open -= 1
        # if not open anymore, close
        if not self.open:
            # save changes
            if self.changed:
                self.block["inventory"] = self.inventory
                self.block.save()
            # remove references
            self.inventory = None
            self.block = None
            
    def replace(self, index, value):
        assert self.open
        self.changed = True
        return self.inventory.replace(index, value)

    def register_callback(self, callback):
        assert callback not in self.observers
        area = Point(self.position)
        observer = self.world.event_system.new_observer(callback,area,"block_update")
        self.observers[callback] = observer

    def unregister_callback(self, callback):
        observer = self.observers.pop(callback)
        self.world.event_system.del_observer(observer)

    def __del__(self):
        assert not self.observers

class EntityInventoryWrapper(InventoryWrapper):
    def __init__(self, inventory):
        super().__init__()
        self.inventory = inventory

    def __eq__(self, other):
        return self.inventory is other.inventory

    def register_callback(self, callback):
        self.inventory.register_callback(callback,False)

    def unregister_callback(self, callback):
        self.inventory.unregister_callback(callback)

class EmptyInventoryWrapper(InventoryWrapper):
    def __bool__(self):
        return False
    def register_callback(self, callback):
        pass
    def unregister_callback(self, callback):
        pass

def inventory_wrapper_factory(inventory_pointer):
    if inventory_pointer == None:
        return EmptyInventoryWrapper()
    elif isinstance(inventory_pointer, (ObservableList,ObservableDict)):
        return EntityInventoryWrapper(inventory_pointer)
    elif isinstance(inventory_pointer, tuple) and len(inventory_pointer) == 2 and\
        isinstance(inventory_pointer[0], World) and isinstance(inventory_pointer[1], Vector):
        return BlockInventoryWrapper(*inventory_pointer)
    else:
        raise ValueError("invalid inventory_pointer type %s" % type(inventory_pointer))

class InventoryDisplay():
    def __init__(self,player):
        self.player = player
        self.is_open = False #Full inventory or only hotbar
        self.inventory = EmptyInventoryWrapper()
        self.foreign_inventory = EmptyInventoryWrapper()
        self.current_pages = [0,0]

    def register(self, inventory_pointer):
        self.unregister()
        self.inventory = inventory_wrapper_factory(inventory_pointer)
        self.inventory.register_callback(self.callback)
        self.display()
    def unregister(self):
        self.inventory.unregister_callback(self.callback)

    def callback(self,inventory):
        self.display()

    def _calculate_index(self,k,row,col):
        if k == 0 and row == 0:
            return row*7 + col #dont scroll away hotbar
        return self.current_pages[k]*7 + row*7 + col

    def display(self):
        size = (0.1,0.1)
        rows = 4# if self.foreign_inventory else 9
        left_hand_slot_visible = False
        right_hand_slot_visible = False
        for k, inventory in enumerate((self.inventory, self.foreign_inventory)):
            with inventory:
                for col in range(7):
                    for row in range(rows):
                        name = "inventory:(%i,%i,%i)" %(k,col,row)
                        if inventory and (self.is_open or k + row == 0):
                            i = self._calculate_index(k,row,col)
                            item = inventory.get(i,None)
                            if item:
                                x = 0.2*(col - 3)
                                y = 0.2*(row) + k - 0.8
                                border = None
                                if k == 0:
                                    if self.is_open and row == 0 and self.current_pages[0] != 0:
                                        y -= 0.05
                                    if i == self.player.entity["left_hand"]:
                                        border = "inventory_border_left"
                                        left_hand_slot_visible = True
                                    if i == self.player.entity["right_hand"]:
                                        border = "inventory_border_right" if (border == None) else "inventory_border_mixed"
                                        right_hand_slot_visible = True
                                position = (x,y,0)
                                self.player.display_item(name,item,position,size,INNER|CENTER,border)
                                continue
                        self.player.undisplay_item(name)
                if inventory and self.is_open:
                    self.player.set_hud("#inventory:(%s,%s)" %(k,+1),"ARROW",(0.8,k-0.4,0),0,size,INNER|CENTER)
                    self.player.set_hud("#inventory:(%s,%s)" %(k,-1),"ARROW",(0.8,k-0.6,0),180,size,INNER|CENTER)
                else:
                    self.player.del_hud("#inventory:(%s,%s)" %(k,-1))
                    self.player.del_hud("#inventory:(%s,%s)" %(k,+1))

        if self.inventory:
            with self.inventory:
                dual_wielding = self.player.entity["left_hand"] == self.player.entity["right_hand"]
                item = self.inventory[self.player.entity["left_hand"]]
                if not left_hand_slot_visible and item["id"] != "AIR":
                    border = "inventory_border_mixed" if dual_wielding else "inventory_border_left"
                    self.player.display_item("left_hand",item,(-0.8,-0.8,0.5),(0.1,0.1),BOTTOM|LEFT,border)
                else:
                    self.player.undisplay_item("left_hand")
                item = self.inventory[self.player.entity["right_hand"]]
                if not right_hand_slot_visible and item["id"] != "AIR" and not dual_wielding:
                    self.player.display_item("right_hand",item,(0.8,-0.8,0.5),(0.1,0.1),BOTTOM|RIGHT,"inventory_border_right")
                else:
                    self.player.undisplay_item("right_hand")


    def open(self,foreign_inventory_pointer = None):
        if self.is_open:
            self.close()
        self.is_open = True
        self.player.focus_hud()
        if foreign_inventory_pointer != None:
            self.foreign_inventory = inventory_wrapper_factory(foreign_inventory_pointer)
            if self.foreign_inventory != self.inventory:
                self.foreign_inventory.register_callback(self.callback)
            self.current_pages[1] = 0
        self.display()

    def close(self):
        if not self.is_open:
            return
        self.is_open = False
        if self.foreign_inventory:
            if self.foreign_inventory != self.inventory:
                with self.foreign_inventory:
                    self.foreign_inventory.on_close()
                self.foreign_inventory.unregister_callback(self.callback)
            self.foreign_inventory = EmptyInventoryWrapper()
        self.display()
    
    def toggle(self):
        if self.is_open:
            self.close()
        else:
            self.open()
            
    def handle_click(self,button,element_id):
        if not (element_id and element_id.startswith("#inventory")):
            return
        hand = button+"_hand"
        args = element_id.rsplit("(",1)[1].split(")",1)[0].split(",")
        if len(args) == 3:
            k, col, row = map(int,args)
            if k == 0:
                self.player.entity[hand] = self._calculate_index(k,row,col)
        else:
            k, direction = map(int,args)
            #inventory = self.inventory if k==0 else self.foreign_inventory
            self.scroll(k, direction)

    def scroll(self, page, direction):
        self.current_pages[page] = max(0,self.current_pages[page] + direction)
        self.display()
    
    def _element_to_inventory_and_index(self, element):
        if element:
            if element.startswith("#inventory"):
                args = element.rsplit("(",1)[1].split(")",1)[0].split(",")
                if len(args) == 3:
                    k, col, row = map(int, args)
                    inventory = self.inventory if k==0 else self.foreign_inventory
                    index = self._calculate_index(k, row, col)
                    return inventory, index
            if element in ("#left_hand", "#right_hand"):
                return self.inventory, self.player.entity[element[1:]]
        return None

    def handle_drag(self,button,from_element,to_element):
        from_inventory_and_index = self._element_to_inventory_and_index(from_element)
        to_inventory_and_index = self._element_to_inventory_and_index(to_element)
        if not from_inventory_and_index or not to_inventory_and_index:
            if from_element:
                print("drop", from_element, "(not implemented)")
            return
        from_inventory, from_index = from_inventory_and_index
        to_inventory, to_index = to_inventory_and_index
        if False: #check if they could stack
            pass #add them together
        else: #swap
            self.swap(from_inventory, from_index, to_inventory, to_index)
    
    def swap(self,inventory1,index1,inventory2,index2):
        with inventory1:
            with inventory2:
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

class ChatDisplay(object):
    def __init__(self, player):
        self.player = player
        self.log = []
        self.current_text = ""
        self.display()
        
    def add_message(self, message):
        self.log.append((time.time(),message))
        self.display()

    def display(self, t0 = 0):
        text = "\n"+"\n".join(m for t,m in self.log if t > t0) #extra linebreak at start to force mulitline mode in client
        if text == self.current_text:
            return
        self.current_text = text
        position = Vector(0.05, 0.1, 0.5)
        rotation = 0
        size = (0.9,0.7)
        align = INNER|TOP|LEFT
        self.player.set_hud_text("chat",text,position,rotation,size,align)
        #self.player.set_hud("chat_bg","STONE",position+(0,0,-0.1),rotation,size,align)


class Player(voxelengine.Player):
    RENDERDISTANCE = 10
    CUSTOM_COMMANDS = {"clicked","dragged"}

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.set_focus_distance(8)
        self.inventory_display = InventoryDisplay(self)
        self.chat = ChatDisplay(self)
        self.gamemode = config["gamemode"]
        self.ongoing_hand_actions = {"left_hand":None, "right_hand":None} #generators that are fed with current hand pressure

    def create_character(self):
        world = self.universe.get_spawn_world()
        character = resources.EntityFactory({"type":"Mensch"})
        character.set_world(world,world.blocks.world_generator.spawnpoint)

        if self.gamemode == "creative":
            items = [
                {"id":"InstaPick"},
                {"id":"Fence","count":100},
                {"id":"SAND","count":100},
                {"id":"GLAS","count":100},
                {"id":"CHEST"},
                {"id":"Fertilizer","count":1000},
                {"id":"Saddle"},
                {"id":"Setzling"},
                {"id":"HEBEL"},
                {"id":"LAMP"},
                {"id":"TORCH"},
                {"id":"FAN"},
                {"id":"Redstone","count":128},
                {"id":"Repeater"},
                ]
            functional = lambda i: (i in resources.Block.subclasses) or (i in resources.Item.subclasses)
            for b in (True, False):
                for itemname in resources.allItemnames:
                    if functional(itemname) == b:
                        items.append({"id":itemname})
        if self.gamemode == "survival":
            items = [
                {"id":"Axe"},
                {"id":"Setzling"},
                {"id":"String","count":100},
                {"id":"Arrow","count":100},
                {"id":"Fishing_Rod"},
                ]
        #filter for items available in selected resource packs and apply
        character["inventory"] = [item for item in items if item["id"] in resources.allItemnames and item["id"] != "missing_texture"]

        # inventory stuff
        for i in range(60):
            character["inventory"].append({"id":"AIR","count":i})
        return character

    def control(self, entity):
        if self.entity:
            self.entity.unregister_item_callback(self._open_inventory_callback,"open_inventory")
            self.entity.unregister_item_callback(self.inventory_display.callback,"left_hand")
            self.entity.unregister_item_callback(self.inventory_display.callback,"right_hand")
            self.entity.unregister_item_callback(self._update_hearts,"health")
        super().control(entity)
        if self.entity:
            self.entity.foreign_inventory = None
            self.inventory_display.register(self.entity["inventory"])
            self.entity.register_item_callback(self._open_inventory_callback,"open_inventory")
            self.entity.register_item_callback(self.inventory_display.callback,"left_hand")
            self.entity.register_item_callback(self.inventory_display.callback,"right_hand")
            self.entity.register_item_callback(self._update_hearts,"health")

    def handle_events(self, events):
        other_events = []
        for event in events:
            if event.tag == "chat":
                self.chat.add_message(event.data)
            else:
                other_events.append(event)
        super().handle_events(other_events)

    def autocomplete(self, msg):
        if msg.startswith("/"):
            command_text = msg[1:]#msg.removeprefix("/")
            ctx = resources.CommandContext(self)
            suggestions = ctx.autocomplete(command_text)
            return ["/"+s for s in suggestions]
        else:
            return ["Hi",
                    "😀","😁","😅","😇","😉","😊","😋","😍","😎",
                    "😐","😓","😕","😚","😛","😜","😟","😠","😢",
                    "😤","😭","😯","😳","😴","🙁","🙂","🙃","🙄",
                    ]

    def _open_inventory_callback(self, boolean):
        if boolean:
            self.inventory_display.open(self.entity.foreign_inventory)
            self.entity.foreign_inventory = None
        else:
            self.inventory_display.close()
    def _update_hearts(self, health):
        #todo: fix!
        for x in range(health,10):
            self.del_hud("heart"+str(x))
        for x in range(health):
            self.set_hud("heart"+str(x),"heart",Vector((-0.95+x/10.0,0.95,0)),0,(0.05,0.05),INNER|LEFT)

    def update(self):
        for msg in self.new_chat_messages():
            if msg.strip():
                name = repr(self)
                if self.entity:
                    name = self.entity.get("id",name)
                print("[%s][%s] %s" % (time.strftime("%Z %Y-%m-%d %T"), name, msg))
                if msg.startswith("/"):
                    command_text = msg[1:]#msg.removeprefix("/")
                    ctx = resources.CommandContext(self)
                    ctx.execute(command_text)
                    #self.chat.add_message(msg)
                else:
                    if self.world:
                        if self.entity:
                            area = Sphere(self.entity["position"],1)
                        else:
                            area = SOMEWHERE
                        event = Event("chat",area,"[%s] %s"%(name,msg))
                        self.world.event_system.add_event(event)
                    else:
                        print("Player want's to say something but is not in any world.")
            else: #empty messages are only sent to player himself, so he can push up the chat if he want's to
                self.chat.add_message("")
        
        if not self.entity:
            return
        pe = self.entity

        if self.was_pressed("fly"):
            if self.gamemode == "creative":
                pe["flying"] = not pe["flying"]
            else:
                self.chat.add_message("Flying is only allowed in creative mode.")
        if self.was_pressed("inv"):
            self.inventory_display.toggle()
        if self.was_pressed("emote") or self.was_released("emote"):
            pe["show_emote"] = self.is_pressed("emote")

        for inv_slot in range(10):
            if self.was_pressed("inv%i"%inv_slot):
                hand = "left_hand" if self.is_pressed("shift") else "right_hand"
                pe[hand] = inv_slot
                pe.select_emote(inv_slot)

        for button, element_id in self.new_custom_commands_dict["clicked"]:
            if button in ("left", "right"):
                self.inventory_display.handle_click(button, element_id)
        for button, element_from, element_to in self.new_custom_commands_dict["dragged"]:
            if button in ("left", "right"):
                self.inventory_display.handle_drag(button, element_from, element_to)
        inv_inc = self.was_pressed("inv+") - self.was_pressed("inv-")
        if inv_inc != 0:
            if self.inventory_display.is_open:
                self.inventory_display.scroll(0, inv_inc)
            else:
                hand = "left_hand" if self.is_pressed("shift") else "right_hand"
                inv_slot = pe[hand] + inv_inc
                inv_slot %= 7
                pe[hand] = inv_slot
            
                

        #if not self.is_active(): # freeze player if client doesnt respond
        #    return

        # target    block                 entity                air
        # no shift  block.clicked         item.use_on_entity    item.use_on_air
        # shift     item.use_on_block     entity.clicked        item.use_on_air

        for event_name in ("left_hand", "right_hand"):
            if self.was_pressed(event_name):
                d_block, pos, face = self.entity.get_focused_pos(self.focus_distance)
                d_entity, entity = self.entity.get_focused_entity(self.focus_distance)

                item_index = pe[event_name]
                item_data = pe["inventory"][item_index]
                item = resources.ItemFactory(item_data)

                # nothing to click on
                if (d_block == None) and (d_entity == None):
                    do_next = item.use_on_air(pe)
                
                # click on block
                elif (d_block != None) and ((d_entity == None) or (d_block < d_entity)):
                    block = pe.world.blocks[pos]
                    if not self.is_pressed("shift"):
                        do_next = block.clicked(pe, face, item)
                    else:
                        do_next = item.use_on_block(pe, block, face)
                
                # click on entity
                else:
                    if not self.is_pressed("shift"):
                        do_next = item.use_on_entity(pe, entity)
                    else:
                        do_next = entity.clicked(pe, item)
                
                if isinstance(do_next, collections.abc.Generator):
                    try:
                        next(do_next) # go up to initial yield so we can use send after
                    except StopIteration: # iterators can finish without a single yield
                        pass
                    else:
                        self.ongoing_hand_actions[event_name] = do_next
            
            if self.ongoing_hand_actions[event_name]:
                pressure = self.get_pressure(event_name)
                try:
                    self.ongoing_hand_actions[event_name].send(pressure)
                except StopIteration:
                    self.ongoing_hand_actions[event_name] = None
                if pressure == 0:
                    self.ongoing_hand_actions[event_name] = None
        
        if self.was_pressed("pickblock"):
            _, pos, _ = self.entity.get_focused_pos(self.focus_distance)
            if pos:
                block = self.entity.world.blocks[pos]
                inv_slot = self.entity.find_inventory_slot(block.item_version())
                if inv_slot:
                    hand = "left_hand" if self.is_pressed("shift") else "right_hand"
                    pe[hand] = inv_slot

        # Movement
        
        nv = Vector(0,0,0)
        sx,sy,sz = pe.get_sight_vector()
        nv += Vector( sx,0, sz) * self.get_pressure("for")
        nv += Vector(-sx,0,-sz) * self.get_pressure("back")
        nv += Vector(-sz,0, sx) * self.get_pressure("right")
        nv += Vector( sz,0,-sx) * self.get_pressure("left")
        
        just_stopped = self.was_released("for") or self.was_released("back") or self.was_released("right") or self.was_released("left")
        if nv != (0,0,0) or just_stopped:
            pe.ai_commands["x"].append(nv[0])
            pe.ai_commands["z"].append(nv[2])
        
        if self.is_pressed("jump"):
            pe.ai_commands["jump"].append(1)
        if self.is_pressed("shift"):
            pe.ai_commands["shift"].append(1)
        if self.is_pressed("sprint"):
            pe.ai_commands["sprint"].append(1)
        
        if pe["rotation"] != self.rotation:
            pe.ai_commands["yaw"].append(self.rotation[0])
            pe.ai_commands["pitch"].append(self.rotation[1])

    def display_item(self,name,item,position,size,align,border=None):
        w, h = size
        self.set_hud(name+"_bgbox","inventory_background",position+Vector((0,0,-0.01)),0,size,align)
        self.set_hud("#"+name,item["id"],position,0,Vector(size)*0.8,align)
        if border:
            self.set_hud(name+"_border",border,position+Vector((0,0,0.01)),0,Vector(size)*1.1,align)
        else:
            self.del_hud(name+"_border")
        self.set_hud_text(name+"_count",str(item.get("count","")),position+Vector((0,0,0.02)),0,size,align)

    def undisplay_item(self,name):
        for prefix, suffix in (("","_bgbox"),("#",""),("","_border"),("","_count")):
            self.del_hud(prefix+name+suffix)

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
        super(World,self).__init__(*args,**kwargs,
                                   blockFactory=resources.BlockFactory,
                                   entityFactory=resources.EntityFactory)
        
        self.set_requests = collections.defaultdict(list) # position: [Request,...]
        self.move_requests = [] # (position_from, position_to)
        
    #def get_block(self,position,*args,**kwargs):
    #    global blockread_counter
    #    blockread_counter += 1
    #    return super(World,self).get_block(position,*args,**kwargs)

    def tick(self, dt):
        super(World,self).tick(dt)
        self.handle_block_requests()
        self.event_system.process_events() # again for events triggered by block requests

    def random_ticks_at(self, position, radius = 10, tries = 1):
        #rate = 0.01
        #tickable_blocks = self.blocks.find_blocks(Sphere(position, radius), "random_tick")
        #for block in tickable_blocks:
        #    if random.random() < rate:
        #        self.random_tick_at(block.position)
        for _ in range(tries):
            tick_position = position + Vector([(random.random()*2-1)*radius for _ in range(DIMENSION)])
            self.random_tick_at(tick_position)
    
    def random_tick_at(self, position):
        random_tick = Event("random_tick", Point(position))
        self.event_system.add_event(random_tick)

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

    def request_set_block(self, position, block, priority=0, valid_tag=None, exclusive=True):
        if valid_tag == None:
            valid_tag = ValidTag()
        self.set_requests[position].append(Request(block, priority, valid_tag, exclusive))
        return valid_tag

class Timer(object):
    def __init__(self):
        self.t = time.time() # timestamp of last tick
        self.dt = None # length of last tick
        self.dt_work = None
        self.dt_idle = None
    def tick(self, TPS):
        spt = 1.0/TPS
        self.dt_work = time.time() - self.t #time since last tick
        self.dt_idle = max(0, spt - self.dt_work)
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
    resources.load_features_from(config["feature_paths"])
    worldtype_paths = {}
    for feature_path in config["feature_paths"]:
        worldtypes_dir = os.path.join(PATH,"features",feature_path,"Welten")
        if os.path.isdir(worldtypes_dir):
            worldtype_names = os.listdir(worldtypes_dir) #everything before feature_path is dropped in case of absolute path
            for worldtype_name in worldtype_names:
                if worldtype_name.endswith(".py") or worldtype_name.endswith(".js"):
                    worldtype_name = worldtype_name[:-3]
                    worldtype_paths[worldtype_name] = os.path.join(worldtypes_dir, worldtype_name)
    savegamepath = config["file"]
    if os.path.exists(savegamepath):
        print("== Loading World ==")
        with open(savegamepath) as savegamefile:
            data = voxelengine.Universe.parse_data_from_string(savegamefile.read())
        u = voxelengine.Universe(data, WorldFactory=World)
        #w = u.new_world(data, WorldClass=World)
    else:
        print("== Preparing World ==")
        data = copy.deepcopy(voxelengine.server.world_data_template.data)
        generator_data = data["block_world"]["generator"]
        generator_data["name"] = config["worldtype"]
        generator_data["seed"] = random.getrandbits(32)
        generator_data["path"] = worldtype_paths[config["worldtype"]]
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
        u = voxelengine.Universe(WorldFactory=World)
        w = u.new_world(data)
        print("== Initialising world ==", flush=True)
        t = time.time()
        w.blocks.world_generator.init(w)
        w.event_system.clear_events()
        dt = time.time() - t
        print("(", len(w.blocks.block_storage.structures), "blocks in", dt, "s )")

    def save():
        print("Preparing Savestate", flush=True)
        data = u.serialize()
        data_string = repr(data)
        print("Checking Savestate ... ", end="", flush=True)
        try:
            voxelengine.Universe.parse_data_from_string(data_string)
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
#        config["save"] = False

    settings = {"wait" : False,
                "name" : config["name"],
                "parole" : config["parole"],
                "subnet_whitelist" : config["whitelist"],
                "texturepack_path" : resources.texturepackPath,
                "PlayerClass" : Player,
                "host" : config["host"],
                "http_port" : config["http_port"],
                "nameserveraddr" : config["nameserver"] if config["public"] else None,
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
                elif command == "kill":
                    print("Game killed")
                    return
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
                elif command.startswith("/"):
                    print(repr(command))
                    cmd = cmd[1:]#command.removeprefix("/")
                    ctx = resources.CommandContext(u)
                    if cmd.endswith("\t"):
                        cmd = cmd.rstrip("\t")
                        print("\n".join("/"+s for s in ctx.autocomplete(cmd)))
                    else:
                        ctx.execute(cmd)                        
                else:
                    print("valid commands include: quit, kill, save, reload, stats, play, /help")
            
            # game server update - communicate with clients
            g.update()

            # to idle or not to idle
            TPS = config["tps"] if g.get_players() else config["idle_tps"]
            if TPS == 0:
                timer.tick(2)
                continue

            # player update
            for player in g.get_players():
                player.update()

            # worlds
            for w in u.get_loaded_worlds():
                # mob spawning
                if config["mobspawning"] and len(w.entities.entities) < config["entitylimit"]:
                    for entity_type, entity_class in resources.Entity.subclasses.items():
                        if len(entity_class.instances) < entity_class.LIMIT:
                            x = random.randint(-40,40)
                            y = random.randint(-10,20)
                            z = random.randint(-40,40)
                            p = Vector(x,y,z)
                            if entity_class.test_spawn_conditions(w, p):
                                e = resources.EntityFactory(entity_type)
                                e.set_world(w,p)

                # entity update
                for entity in tuple(w.entities.find_entities(EVERYWHERE, "update")): #M# replace with near player(s) sometime, find a way to avoid need for making copy
                    if entity.world: # make sure it didn't die inbetween of find_entities and now (killed in update of other entity)
                        entity.update()

                # random ticks
                for random_tick_source in w.entities.find_entities(EVERYWHERE, "random_tick_source"):
                    w.random_ticks_at(random_tick_source["position"])

                stats.set("events",sum(map(len, w.event_system.event_queue)))

            # tick
            timer.tick(TPS)
            dt = timer.dt
            if dt > 1:
                print(f"Lag! Last tick took {dt}s. Slowing down game to avoid physics simulation problems at large time delta.")
                dt = 1/TPS
            u.tick(dt)
            
            # Stats
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
    if config["public"] and (config["whitelist"] != ["0.0.0.0/0"]):
        if config["parole"]:
            print("You have a whitelist enabled. Some people may have problem joining even if the know the parole.")
        else:
            raise Exception('Whitelist for public server must be set to ["0.0.0.0/0"].')

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

if os.name == "nt": #Windows
    input_queue = queue.Queue()
    def add_input():
        while True:
            input_queue.put(input())

    input_thread = threading.Thread(target=add_input, args=())
    input_thread.daemon = True
    input_thread.start()

    def get_inputs():
        while not input_queue.empty():
            yield input_queue.get()

else: #Linux
    def get_inputs():
        while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            line = sys.stdin.readline()
            if line:
                yield line.rstrip("\r\n")
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
