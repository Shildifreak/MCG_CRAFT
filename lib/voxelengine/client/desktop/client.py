# -*- coding: cp1252 -*-
# Copyright (C) 2016 - 2020 Joram Brenz
# Copyright (C) 2013 Michael Fogleman

import math
import time, random
import sys, os, inspect
import warnings
from collections import deque, defaultdict
import collections
import itertools, functools
from functools import reduce
import operator
import ast
import threading
import urllib.request
import io
import base64
import ctypes

# Adding directory with modules to python path
PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(os.path.join(PATH,"..","..","modules"))
sys.path.append(os.path.join(PATH,"..","..",".."))
sys.path.append(os.path.join(PATH,".."))

import pyglet
from pyglet import image
#pyglet.options["debug_gl"] = False
#pyglet.options['debug_media'] = True
pyglet.options['shadow_window'] = False
pyglet.options['audio'] = ('openal', 'pulse', 'xaudio2', 'directsound', 'silent')
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse

import client_utils
import socket_connection_7.socket_connection as socket_connection
import world_generation
from shared import *
from shader import Shader
from geometry import Vector, BinaryBox, Box, Point, Ray

RENDERDISTANCE = Vector(2,2,2) # chunks in each direction - e.g. RENDERDISTANCE = (2,2,2) means 5*5*5 = 125 chunks
CHUNKBASE = 4
CHUNKSIZE = 2**CHUNKBASE
TICKS_PER_SEC = 60
MSGS_PER_TICK = 100
ACCEPTABLE_BLOCKFACE_UPDATE_BUFFER_SIZE = CHUNKSIZE**DIMENSION*6
JOYSTICK_DEADZONE = 0.1
FOV = 65.0
ZNEAR = 0.1
ZFAR = 200.0
INITIAL_CAMERA_SMOOTHING = 0

focus_distance = 0

# Mapping of keys to events
KEYMAP = [
    (("key"  , key._1     ),"inv1"      ),
    (("key"  , key._2     ),"inv2"      ),
    (("key"  , key._3     ),"inv3"      ),
    (("key"  , key._4     ),"inv4"      ),
    (("key"  , key._5     ),"inv5"      ),
    (("key"  , key._6     ),"inv6"      ),
    (("key"  , key._7     ),"inv7"      ),
    (("key"  , key._8     ),"inv8"      ),
    (("key"  , key._9     ),"inv9"      ),
    (("key"  , key._0     ),"inv0"      ),
    (("key"  , key.W      ),"for"       ),
    (("key"  , key.S      ),"back"      ),
    (("key"  , key.A      ),"left"      ),
    (("key"  , key.D      ),"right"     ),
    (("key"  , key.SPACE  ),"jump"      ),
    (("key"  , key.TAB    ),"fly"       ),
    (("key"  , key.E      ),"inv"       ),
    (("key"  , key.LSHIFT ),"shift"     ),
    (("key"  , key.LCTRL  ),"sprint"    ),
    (("mouse", mouse.LEFT ),"left_hand" ),
    (("mouse", mouse.MIDDLE),"pickblock"),
    (("mouse", mouse.RIGHT),"right_hand"),
    (("key"  , key.F      ),"emote"     ),
    (("key"  , key.T      ),"chat"      ),
    (("scroll","up"       ),"inv-"      ),
    (("scroll","down"     ),"inv+"      ),
    (("key"  , key.LEFT   ),"-yaw"    ),
    (("key"  , key.RIGHT  ),"+yaw"    ),
    (("key"  , key.DOWN   ),"-pitch"    ),
    (("key"  , key.UP     ),"+pitch"    ),
    ]
import appdirs
configdir = appdirs.user_config_dir("MCGCraft","ProgrammierAG")
configfn = os.path.join(configdir,"desktopclientsettings.py")
print("client config location:",configfn)
if os.path.exists(configfn):
    with open(configfn) as configfile:
        config = eval(configfile.read(),globals())
        if "controls" in config:
            if len(config["controls"]) > 0 and isinstance(config["controls"][0], dict):
                KEYMAP = [(event, action) for control_layer in config["controls"] for action,event in control_layer.items()]
            else:
                KEYMAP = config["controls"]
        else:
            print("no controls found in file, using default controls")
else:
    print("file not found, using default controls")

FACES = [Vector([ 0, 1, 0]), #top
         Vector([ 0,-1, 0]), #bottom
         Vector([ 0, 0, 1]), #front
         Vector([ 0, 0,-1]), #back
         Vector([-1, 0, 0]), #left
         Vector([ 1, 0, 0])] #right
FACES_PLUS = FACES + [Vector([ 0, 0, 0])]

vertex_shader_code = b"""
#version 130

varying vec4 color;

void main()
{
    //normal = gl_NormalMatrix * gl_Normal;
    color = gl_Color;
    gl_Position = ftransform();
    gl_TexCoord[0] = gl_MultiTexCoord0;

    // fog stuff (https://community.khronos.org/t/opengl-fog-and-shaders/52902)
    vec4 eyePos = gl_ModelViewMatrix * gl_Vertex;
    gl_FogFragCoord = abs(eyePos.z/eyePos.w);
}
"""


class TextGroup(pyglet.graphics.OrderedGroup):
    def set_state(self):
        super(TextGroup,self).set_state()
        glDisable(GL_DEPTH_TEST)
    def unset_state(self):
        super(TextGroup,self).unset_state()
        glEnable(GL_DEPTH_TEST)
class ColorkeyGroup(pyglet.graphics.OrderedGroup):
    def set_state(self):
        super(ColorkeyGroup,self).set_state()
        glDisable(GL_CULL_FACE)
        glEnable(GL_ALPHA_TEST)
        glAlphaFunc(GL_GREATER, 0)
    def unset_state(self):
        super(ColorkeyGroup,self).unset_state()
        glEnable(GL_CULL_FACE)
        glDisable(GL_ALPHA_TEST)
textgroup = TextGroup(2)
colorkey_group = ColorkeyGroup(1)
normal_group = pyglet.graphics.OrderedGroup(0)

def cube_vertices(x, y, z, n):
    """ Return the vertices of the cube at position x, y, z with size 2*n.

    """
    return [
        x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n, x-n,y+n,z-n,  # top
        x+n,y-n,z+n, x-n,y-n,z+n, x-n,y-n,z-n, x+n,y-n,z-n,  # bottom
        x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n,  # front
        x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n,  # back
        x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n,  # left
        x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n,  # right
    ]

def face_vertices(x, y, z, f, n):
    return (
        [x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n, x-n,y+n,z-n],  # top
        [x+n,y-n,z+n, x-n,y-n,z+n, x-n,y-n,z-n, x+n,y-n,z-n],  # bottom
        [x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n],  # front
        [x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n],  # back
        [x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n],  # left
        [x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n],  # right
    )[f]

def face_vertices_noncube(x, y, z, f, size):
    dx,dy,dz = size
    return (
        [x-dx,y+dy,z+dz, x+dx,y+dy,z+dz, x+dx,y+dy,z-dz, x-dx,y+dy,z-dz],  # top
        [x+dx,y-dy,z+dz, x-dx,y-dy,z+dz, x-dx,y-dy,z-dz, x+dx,y-dy,z-dz],  # bottom
        [x-dx,y-dy,z+dz, x+dx,y-dy,z+dz, x+dx,y+dy,z+dz, x-dx,y+dy,z+dz],  # right
        [x+dx,y-dy,z-dz, x-dx,y-dy,z-dz, x-dx,y+dy,z-dz, x+dx,y+dy,z-dz],  # left
        [x-dx,y-dy,z-dz, x-dx,y-dy,z+dz, x-dx,y+dy,z+dz, x-dx,y+dy,z-dz],  # front
        [x+dx,y-dy,z+dz, x+dx,y-dy,z-dz, x+dx,y+dy,z-dz, x+dx,y+dy,z+dz],  # back
    )[f]

def tex_coord(x, y, dx = 1, dy = 1):
    """ Return the bounding vertices of the texture square.

    """
    p = TEXTURE_EDGE_CUTTING
    x += p
    y += p
    dx -= 2 * p
    dy -= 2 * p

    mx = 1.0 / TEXTURE_DIMENSIONS[0]
    my = 1.0 / TEXTURE_DIMENSIONS[1]
    x  *= mx
    y  *= my
    dx *= mx
    dy *= my

    return x, y, x + dx, y, x + dx, y + dy, x, y + dy


def cube_model(textures,n,sidehiding):
    """ Return a list of the texture squares for the top, bottom and side.

    """
    result = []
    for f in range(6):
        fv = face_vertices(0,0,0,f,n)
        if f >= len(textures):
            f = -1
        texture = tex_coord(*textures[f])
        result.append((fv,texture))
    result.append(([],()))
    if not sidehiding:
        all_in_one = reduce(lambda a,b:(a[0]+b[0],a[1]+b[1]),result)
        return (([],()),)*6+(all_in_one,)
    return tuple(result)

def block_model(vertices, textures):
    sides = zip(vertices, textures)
    result = []
    for raw_side_vertices, raw_side_textures in sides:
        side_vertices = []
        side_textures = []
        for raw_face_vertices in raw_side_vertices:
            for coord in raw_face_vertices:
                side_vertices.append(coord-0.5)
        for raw_face_textures in raw_side_textures:
            side_textures.extend(tex_coord(*raw_face_textures))
        result.append((side_vertices,side_textures))
    return result

class BlockModelDict(dict):
    def __missing__(self, key):
        parts = key.rsplit(":",1)
        if len(parts) == 2:
            blockid, state = parts
            baseModel = self[blockid]
            model = self.rotate(baseModel, state)
            self[key] = model
            return model
        return self["missing_texture"]

    @staticmethod
    def rotate(model,state):
        if "1" in state:
            c = 3
        elif "2" in state:
            c = 2
        elif "3" in state:
            c = 1
        else:
            c = 0
        model = tuple((list(vertices),text_coords) for vertices, text_coords in model)
        def r_x(model):
            top, bottom, front, back, left, right, other = model
            model = back, front, top, bottom, left, right, other
            for vertices, text_coords in model:
                for i in range(0,len(vertices),3):
                    vertices[i+1],vertices[i+2] = -vertices[i+2],  vertices[i+1]
            return model
        def r_y(model):
            top, bottom, front, back, left, right, other = model
            model = top, bottom, left, right, back, front, other
            for vertices, text_coords in model:
                for i in range(0,len(vertices),3):
                    vertices[i+0],vertices[i+2] =  vertices[i+2], -vertices[i+0]
            return model
        for _ in range(c):
            model = r_y(model)
        #  e
        #n   s
        #  w
        if "t" in state:
            model = r_x(r_x(model))
            return model
        if "n" in state:
            c = 0
        elif "e" in state:
            c = 3
        elif "s" in state:
            c = 2
        elif "w" in state:
            c = 1
        else:
            return model
        model = r_x(model)
        for _ in range(c):
            model = r_y(model)
        return model
        
def load_setup(host, port):
    global BLOCKMODELS, TRANSPARENCY, TEXTURE_DIMENSIONS, TEXTURE_URL, TEXTURE_EDGE_CUTTING, ENTITY_MODELS, ICON, BLOCKNAMES, SOUNDS, FOG, CONNECTED
    def url_for(filename, folder="desktop"):
        path = "/".join(("/texturepacks",folder,filename))
        netloc = "%s:%i" % (host,port)
        components = urllib.parse.ParseResult("http",netloc,path,"","","")
        url = urllib.request.urlunparse(components)
        return url
    with urllib.request.urlopen(url_for("description.py")) as descriptionfile:
        description = ast.literal_eval(descriptionfile.read().decode()) #specify encoding? (standart utf-8)
    TEXTURE_DIMENSIONS = description["TEXTURE_DIMENSIONS"]
    TEXTURE_EDGE_CUTTING = description.get("TEXTURE_EDGE_CUTTING",0)
    ENTITY_MODELS = description.get("ENTITY_MODELS",{})
    TEXTURE_URL = url_for("textures.png")
    TRANSPARENCY = {"AIR":True}
    CONNECTED = {}
    FOG = {}
    ICON = collections.defaultdict(lambda:ICON["missing_texture"])
    BLOCKMODELS = BlockModelDict()
    BLOCKNAMES = []
    for name, transparency, connected, fog, icon_coords, vertices, textures in description["BLOCK_MODELS"]:
        BLOCKMODELS[name] = block_model(vertices, textures)
        ICON[name] = tex_coord(*icon_coords)
        TRANSPARENCY[name] = transparency
        CONNECTED[name] = connected
        FOG[name] = fog
    
    SOUNDS = {}
    sound_files = {}
    for filename in set(description["SOUNDS"].values()):
        url = url_for(filename,folder="sounds")
        with urllib.request.urlopen(url) as f:
            b = io.BytesIO(f.read())
        sound_files[filename] = pyglet.media.StaticSource(pyglet.media.load(filename,b))
    for sound, filename in description["SOUNDS"].items():
        SOUNDS[sound] = sound_files[filename]

def is_transparent(block_name):
    return TRANSPARENCY.get(block_name.rsplit(":",1)[0],0)

def is_connected(block_name):
    return CONNECTED.get(block_name.rsplit(":",1)[0],False)

def get_fog(block_name):
    return FOG.get(block_name.rsplit(":",1)[0],(255,255,255,0))

#M# improve order of chunkpositions for better caching!
CHUNKPOSITIONS = tuple(map(Vector, itertools.product(range(CHUNKSIZE),repeat=DIMENSION)))
iterchunk = CHUNKPOSITIONS.__iter__

def iterframe():
    for de in (-1,CHUNKSIZE):
        for d1 in range(CHUNKSIZE):
            for d2 in range(CHUNKSIZE): # faces
                yield (de,d1,d2)
                yield (d1,de,d2)
                yield (d1,d2,de)
        for df in (-1,CHUNKSIZE):
            for d1 in range(CHUNKSIZE): # edges
                yield (d1,de,df)
                yield (de,d1,df)
                yield (de,df,d1)
            for dg in (-1,CHUNKSIZE):    # corners
                yield (de,df,dg)

class BlockStorage(object): # make this a dict itself?
    def __init__(self):
        self.terrain_function = lambda position:"AIR"
        self.blocks = {}

    @functools.lru_cache()
    def get_block(self,position):
        return self.blocks.get(position,None) or self.terrain_function(position)

    def set_block(self,position,value):
        if value == self.terrain_function(position):
            self.blocks.pop(position, None) #possible that position is not in blocks when defaultblock gets set twice
        else:
            self.blocks[position] = value
        self.get_block.cache_clear()

    def set_terrain_function(self, terrain_function):
        self.terrain_function = terrain_function
        self.get_block.cache_clear()

    def clear(self):
        self.blocks = {}
        self.get_block.cache_clear()

class ChunkManager(object):
    def __init__(self):
        self.unmonitored_since_ids = defaultdict(int) #chunkposition : monitor update id
        self.current_monitor_id = 0
        self.monitored_chunks = set()
        self._last_center_chunk_position = None
    
    def monitor_around(self, center_chunk_position):
        """returns (added, removed) two sets of chunkpositions"""
        if center_chunk_position != self._last_center_chunk_position:
            self._last_center_chunk_position = center_chunk_position

            offsets = itertools.product(*(range(-r, r+1) for r in RENDERDISTANCE))
            new = set(center_chunk_position + offset for offset in offsets)
            removed = self.monitored_chunks - new
            added = new - self.monitored_chunks        
            self.monitored_chunks = new
            
            self.current_monitor_id += 1
            for chunkpos in removed:
                self.unmonitored_since_ids[chunkpos] = self.current_monitor_id

            return added, removed
        return set(), set()

    def clear(self):
        self.unmonitored_since_ids = defaultdict(int)
        #self.current_monitor_id = 0
        self.monitored_chunks = set()
        self._last_center_chunk_position = None
    
    def has_blocks_to_be_updated(self):
        pass
    
    def get_block_to_be_updated(self):
        pass

class SetQueue(collections.OrderedDict):
    def add(self, value):
        self[value] = None
    def popleft(self):
        return self.popitem(last=False)[0]

class InitChunkQueue(object):
    def __init__(self, chunk_priority_callback):
        self.committed = set()
        self.chunks = set()
        self.positions = []
        self.world_generator = None
        self.chunk_priority_callback = chunk_priority_callback
    def clear(self):
        self.committed.clear()
        self.chunks.clear()
        self.positions.clear()
        self.world_generator = None
    def _refill(self):
        if self.chunks:
            chunk = min(self.chunks, key=self.chunk_priority_callback)
            self.chunks.remove(chunk)
            self.committed.add(chunk)
            self.positions = [(chunk << CHUNKBASE) + offset for offset in CHUNKPOSITIONS]
            self.world_generator.preload(self.positions)
        else:
            raise Exception("can't call _refill with empty chunks")
    def add(self, chunk):
        if chunk in self.committed or chunk in self.chunks:
            pass
        else:
            if self.world_generator.terrain_hint((CHUNKBASE,chunk),"visible"):
                self.chunks.add(chunk)
    def difference_update(self, remove_set):
        self.chunks.difference_update(remove_set)
    def update(self, add_set):
        for chunk in add_set:
            self.add(chunk)
    def is_empty(self):
        return not (self.chunks or self.positions)
    def pop(self):
        if not self.positions:
            self._refill()
        return self.positions.pop()

class Model(object):

    def __init__(self, chunk_priority_callback):

        # A Batch is a collection of vertex lists for batched rendering.
        self.batch = pyglet.graphics.Batch()
        self.hud_batch = pyglet.graphics.Batch()

        # A TextureGroup manages an OpenGL texture.
        with urllib.request.urlopen(TEXTURE_URL) as texture_stream:
            texture_buffer = io.BytesIO(texture_stream.read())
            texture = image.load("", file=texture_buffer).get_texture() #possible to use image.load(file=filedescriptor) if necessary
        self.textured_normal_group = TextureGroup(texture, parent = normal_group) 
        self.textured_colorkey_group = TextureGroup(texture, parent = colorkey_group)

        self.shown = {} #{(position,face):vertex_list(batch_element)}
        self.chunks = ChunkManager()
        self.blocks = BlockStorage()
        self.entities = {} #{entity_id: (vertex_list,...,...)}
        self.hud_elements = {} #{hud_element_id: (vertex_list,element_data,corners)}

        self.queue = deque()
        self.blockface_update_buffer = SetQueue()
        self.init_chunk_queue = InitChunkQueue(chunk_priority_callback)

        self.occlusion_cache = collections.OrderedDict()
        
        self.load_generator({"code_js":""})

    def add_block(self, position, block_name):
        """for immediate execution use private method"""
        self.queue.append((self._add_block,(position,block_name)))

    def remove_block(self, position):
        """for immediate execution use private method"""
        self.queue.append((self._remove_block,(position,)))

    def clear(self, generator_data):
        """for immediate execution use private method"""
        self.queue.append((self._clear,(generator_data,)))

    def del_area(self, position):
        """for immediate execution use private method"""
        self.queue.append((self._del_area,(position,)))

    def set_area(self, position, codec, compressed_blocks):
        """for immediate execution use private method"""
        self.queue.append((self._set_area,(position,codec,compressed_blocks)))

    def process_queue(self):
        start = time.time()
        while time.time() - start < 1.0 / TICKS_PER_SEC:
            if len(self.blockface_update_buffer) <= ACCEPTABLE_BLOCKFACE_UPDATE_BUFFER_SIZE:
                if self.queue:
                    func, args = self.queue.popleft()
                    func(*args)
                    continue
            if self.blockface_update_buffer:
                position, face = self.blockface_update_buffer.popleft()
                self._update_face(position,face)
                continue
            if not self.init_chunk_queue.is_empty():
                position = self.init_chunk_queue.pop()
                if self.blocks.get_block(position) != "AIR":
                    self.update_visibility(position)
                continue
            break

    def load_generator(self, generator_data):
        self.world_generator = world_generation.WorldGenerator(generator_data, init_py = False)
        self.init_chunk_queue.world_generator = self.world_generator
        self.blocks.set_terrain_function(self.world_generator.client_terrain)

    def monitor_around(self, position):
        """returns list of messages to be send to server in order to announce new monitoring area and required updates"""
        center_chunk_position = position.round() >> CHUNKBASE
        added, removed = self.chunks.monitor_around(center_chunk_position)

        # init queue removed
        self.init_chunk_queue.difference_update(removed)
        self.init_chunk_queue.update(added)

        # monitor
        lowest_corner_chunk = center_chunk_position - RENDERDISTANCE
        highest_corner_chunk = center_chunk_position + RENDERDISTANCE
        lower_bounds = lowest_corner_chunk << CHUNKBASE
        upper_bounds = ((highest_corner_chunk + (1,1,1)) << CHUNKBASE) - (1,1,1)
        yield ("monitor", lower_bounds, upper_bounds, self.chunks.current_monitor_id)
        
        # update and init queue added
        added_chunks_with_areas_and_mid = [(chunkpos,
                                            BinaryBox(CHUNKBASE, chunkpos).bounding_box(),
                                            self.chunks.unmonitored_since_ids[chunkpos])
                                           for chunkpos in added]
        #sort added by distance to position
        added_chunks_with_areas_and_mid.sort(key = lambda x, p=Point(position): x[1].distance(p))

        for chunkpos, area, m_id in added_chunks_with_areas_and_mid:
            # create messages for server
            yield ("update", area.lower_bounds, area.upper_bounds, m_id)


    ########## more private stuff ############

    def ambient_occlusion(self, vertex):
        # see if already cached
        light = self.occlusion_cache.get(vertex,None)
        if light != None:
            return light
        # calculate
        light = 0
        x,y,z = vertex
        for x2 in (int(math.floor(x)),int(math.ceil(x))):
            for y2 in (int(math.floor(y)),int(math.ceil(y))):
                for z2 in (int(math.floor(z)),int(math.ceil(z))):
                    v = Vector((x2,y2,z2))
                    w = abs(reduce(operator.mul,v-vertex))
                    light += is_transparent(self.get_block(v)) * w
        # add to cache
        if False:#len(self.occlusion_cache) > 100:
            self.occlusion_cache.popitem(last=False)
        self.occlusion_cache[vertex] = light
        return light

    def sunlight(self, vertex, face):
        return face[1] #assuming sun is directly above
        
    def color_corrections(self, vertex_data, face):
        """assumes the vertex data is [x,y,z, x,y,z, ...]
        #M# compute face automatically some day
        """
        i = iter(vertex_data)
        color_corrections = []
        for vertex in zip(i,i,i):
            cc = 0.7*self.ambient_occlusion(vertex) + 0.3*self.sunlight(vertex, face)
            color_corrections.extend((cc,cc,cc))
        return color_corrections

    def update_visibility(self, position):
        for f in range(len(FACES_PLUS)):
            self.update_face(position,f)

    def update_face(self,position,face):
        self.blockface_update_buffer.add((position,face))
    
    def _update_face(self,position,face):
        if face >= len(FACES):
            self.show_face(position,face) # always show "inner faces"
        else:
            fv = FACES[face]
            b = self.get_block(position+fv)
            # only show faces facing into transparent blocks and not if blocks are connected and the same
            if is_transparent(b) and not (is_connected(b) and b == self.get_block(position)): #M# maybe get current block as argument instead of by position
                self.show_face(position,face)
            else:
                self.hide_face(position,face)
            
    def update_visibility_around(self,position):
        # faces with visibility influenced
        #for f,fv in enumerate(FACES):
            #self.update_face(position-fv,f)
        
        # faces with lighting influenced
        for f,fv in enumerate(FACES):
            ranges = [range(max(0,fv[i])-1, min(0,fv[i])+2) for i in range(DIMENSION)]
            for offset in itertools.product(*ranges):
                self.update_face(position+offset-fv,f)
    
    def show_face(self,position,face):
        if (position,face) in self.shown:
            self.hide_face(position,face)
            #M# man könnte auch das vorhandene updaten
        #x, y, z = position
        block_name = self.get_block(position)
        if block_name == "AIR":
            return
        vertex_data, texture_data = BLOCKMODELS[block_name][face]
        if not (vertex_data and texture_data):
            return
        vertex_data = tuple(map(sum,zip(vertex_data,itertools.cycle(position))))
        group = self.textured_colorkey_group if is_transparent(block_name) else self.textured_normal_group
        # create vertex list
        # FIXME Maybe `add_indexed()` should be used instead
        length = len(vertex_data)//3
        self.shown[(position,face)] = self.batch.add(length, GL_QUADS, group,
            ('v3f/static', vertex_data),
            ('t2f/static', texture_data),
            ('c3f/static', self.color_corrections(vertex_data,FACES_PLUS[face])))

    def hide(self,position):
        for face in range(len(FACES_PLUS)):
            self.hide_face(position,face)

    def hide_face(self,position,face):
        if not (position,face) in self.shown:
            return False
        self.shown.pop((position,face)).delete()

    @staticmethod
    def _transform(mat,offset,vecs):
        # used in set_entity
        # ignores translation (4th column) of matrix and uses offset instead
        return [sum([vecs[c-(c%3)+r]*mat[r+4*(c%3)] for r in range(3)])+offset[c%3] for c,x in enumerate(vecs)]

    def set_entity(self,entity_id,model_id,position,rotation,model_maps):
        self.del_entity(entity_id)
        if model_id == None:
            return
        vertex_lists=[]
        model = ENTITY_MODELS[model_id]
        # transformationsmatrix bekommen
        glPushMatrix()
        glLoadIdentity()
        x, y = rotation
        glRotatef(x, 0, 1, 0)
        body_matrix = (GLfloat * 16)()
        glGetFloatv(GL_MODELVIEW_MATRIX,body_matrix)
        glPopMatrix()
        glPushMatrix()
        glLoadIdentity()
        glRotatef(-y, 1, 0, 0)#, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        head_matrix = (GLfloat * 16)()
        glGetFloatv(GL_MODELVIEW_MATRIX,head_matrix)
        glPopMatrix()
        glPushMatrix()
        glLoadIdentity()
        glRotatef(math.sin(time.time()*6.2)*20, 1, 0, 0)
        legl_matrix = (GLfloat * 16)()
        glGetFloatv(GL_MODELVIEW_MATRIX,legl_matrix)
        glPopMatrix()
        glPushMatrix()
        glLoadIdentity()
        glRotatef(math.sin(time.time()*6.2)*-20, 1, 0, 0)
        legr_matrix = (GLfloat * 16)()
        glGetFloatv(GL_MODELVIEW_MATRIX,legr_matrix)
        glPopMatrix()
        for modelpart in ("body","head","legl","legr"):
            for relpos,offset,size,block_name in model[modelpart]:
                offset = offset if modelpart in ("head","legl","legr") else relpos
                block_name = model_maps.get(block_name, block_name) #replace block_name if in model_maps
                blockmodel = BLOCKMODELS[block_name]
                group = self.textured_colorkey_group if is_transparent(block_name) else self.textured_normal_group
                for face in range(len(FACES_PLUS)):
                    vertex_data, texture_data = blockmodel[face]
                    #face_vertices_noncube(x, y, z, face, (i/2.0 for i in size))
                    vertex_data = [x*size[c%3]+offset[c%3] for c,x in enumerate(vertex_data)]
                    if modelpart == "head":
                        vertex_data = self._transform(head_matrix,relpos,vertex_data)
                    if modelpart == "legl":
                        vertex_data = self._transform(legl_matrix,relpos,vertex_data)
                    if modelpart == "legr":
                        vertex_data = self._transform(legr_matrix,relpos,vertex_data)
                    vertex_data = self._transform(body_matrix,position,vertex_data)
                    color_data = (0.5,)*len(vertex_data)
                    # create vertex list
                    # FIXME Maybe `add_indexed()` should be used instead
                    try:
                        vertex_lists.append(self.batch.add(len(vertex_data)//3, GL_QUADS, group,
                            ('v3f/static', vertex_data),
                            ('t2f/static', texture_data),
                            ('c3f/static', color_data)))
                    except:
                        print(model_id, model_maps, vertex_data, texture_data, color_data)
                        raise
                    #M# make only one vertex list per entity!
        self.entities[entity_id] = vertex_lists

    def del_entity(self,entity_id):
        vertex_lists = self.entities.pop(entity_id,[])
        for vertex_list in vertex_lists:
            vertex_list.delete()

    def set_hud(self,element_data,window_size):#id,texture,position,rotation,size,align
        element_id,texture,position,rotation_deg,rsize,align = element_data
        if element_id in self.hud_elements:
            self.del_hud(element_id)
        f = (max if OUTER & align else min)(window_size)
        size = f*Vector(rsize)
        center_pos = tuple(((1+bool(align & pa)-bool(align & na))*(ws-f) + (xy+1)*f) / 2
                            for pa,na,ws,xy,si in zip((RIGHT,TOP),(LEFT,BOTTOM),window_size,position,size)
                            ) + (position[2],)
        rotation_rad = math.radians(rotation_deg)
        c = math.cos(rotation_rad)
        s = math.sin(rotation_rad)
        unitoffsets = (-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)
        objoffsets = tuple((uo[0]*size[0],uo[1]*size[1]) for uo in unitoffsets)
        screenoffsets = tuple((c*x - s*y, c*y + s*x) for x,y in objoffsets)

        corners = tuple(c + o
                        for offset in screenoffsets
                        for c, o in zip(center_pos, offset+(0,))
                        )
        #i = iter(corners)
        #corners = [a for b in zip(i,i,(position[2],)*4) for a in b]

        if texture == "AIR":
            vertex_list = None
        elif not texture.startswith ("/"):
            texture_data = list(ICON[texture])
            vertex_list = self.hud_batch.add(4, GL_QUADS, self.textured_colorkey_group,
                            ('v3f/static', corners),
                            ('t2f/static', texture_data))
        else:
            x,y,z = center_pos
            text = texture[1:]
            if not "\n" in text:
                label = pyglet.text.Label(text,x=x,y=y,
                                          anchor_x='center',anchor_y='center',
                                          width=size[0], height=size[1],
                                          batch=self.hud_batch,group=textgroup,
                                          multiline=True, # align only works when multiline = True
                                          align="right",
                                          font_name="Arial"
                                          )
                label.content_valign = "bottom"
            else:
                document = pyglet.text.decode_text(text)
                document.set_style(0, len(document.text), {
                    'font_name': "Arial",
                    #'font_size': font_size,
                    #'bold': bold,
                    #'italic': italic,
                    'color': (255,255,255,255),
                    'align': "left",
                    })
                label = pyglet.text.layout.ScrollableTextLayout(document,
                                          batch=self.hud_batch,group=textgroup,
                                          multiline=True, width=int(size[0]), height=int(size[1]),
                                          )
                label.begin_update()
                
                label.x = int(x)
                label.y = int(y)
                label.anchor_x = "center"
                label.anchor_y = "center"
                
                # doesn't work although it should (bug in pyglet)
                #label.valign = label.height - label.content_height
                #label.content_valign = "bottom"
                
                #M# workaround for bug in pyglet
                label.top_group.view_y = label.height - label.content_height
                
                label.end_update()
                
            vertex_list = label #of course the label isn't simply a vertex list, but it has a delete method, so it should work
        self.hud_elements[element_id] = (vertex_list,element_data,(center_pos, (c, s), size))
        
    def del_hud(self,element_id):
        vertex_list = self.hud_elements.pop(element_id,[None])[0]
        if vertex_list:
            vertex_list.delete()

    def hud_resize(self, window_size):
        for vertex_list,element_data,_ in tuple(self.hud_elements.values()):
            self.set_hud(element_data,window_size)

    def _add_block(self, position, block_name):
        prev_block_name = self.get_block(position)
        self.occlusion_cache.clear()
        self.blocks.set_block(position,block_name)
        self.update_visibility(position)
        #M# todo: make this better (different transparency classes)
        if is_transparent(prev_block_name) or is_transparent(block_name):
            self.update_visibility_around(position)

    def _remove_block(self, position):
        self._add_block(position, "AIR")

    def _clear(self, generator_data):
        #for position,face in self.shown.keys():
        while self.shown:
            position, face = self.shown.popitem()
            self.hide_face(position,face)
        self.shown = {}
        self.blocks.clear()
        self.chunks.clear()
        self.init_chunk_queue.clear()
        self.load_generator(generator_data)

    def _del_area(self, position):
        for relpos in iterchunk():
            self.hide((position<<CHUNKSIZE)+relpos)
        for relpos in iterframe():
            #M# hier müsste eigentlich immer nur die entsprechende Seite upgedated werden
            self.update_visibility((position<<CHUNKSIZE)+relpos)

    def _set_area(self, position, codec, compressed_blocks):
        raise DeprecationWarning("This code doesn't work anymore since Server side chunks have been removed")

        if isinstance(self.chunks[position],Chunk):
            self._del_area(position)
        c = Chunk(CHUNKSIZE,codec)
        self.chunks[position] = c
        c.compressed_data = compressed_blocks
        self.occlusion_cache.clear()

        for i,relpos in enumerate(iterchunk()):
            if c[i] != "AIR": #wird zwar in update_visibility auch noch mal geprüft, ist aber so schneller
                self.queue.appendleft((self.update_visibility,((position<<CHUNKSIZE)+relpos,)))
        for relpos in iterframe():
            #M# hier gilt das selbe wie in _del_chunk
            self.queue.appendleft((self.update_visibility,((position<<CHUNKSIZE)+relpos,)))

    #M# test whether caching helps
    def get_block(self,position):
        return self.blocks.get_block(position)

class JoystickHandler(object):
    def __init__(self, window):
        self.window = window

    def on_joybutton_press(self, joystick, button):
        key = "button_%i"%button
        joystick.states[key] = 255
        self.window.send_input_change(("joystick",key))

    def on_joybutton_release(self, joystick, button):
        key = "button_%i"%button
        joystick.states[key] = 0
        self.window.send_input_change(("joystick",key))

    def on_joyaxis_motion(self, joystick, axis, value):
        self._on_joyaxis_motion(joystick, "trigger_%s"%axis, (value+1)/2)
        self._on_joyaxis_motion(joystick, "+"+axis, +value)
        self._on_joyaxis_motion(joystick, "-"+axis, -value)

    def on_joyhat_motion(self, joystick, hat_x, hat_y):
        joystick_handlers._on_joyaxis_motion(joystick, "+joyhat_x", +hat_x)
        joystick_handlers._on_joyaxis_motion(joystick, "-joyhat_x", -hat_x)
        joystick_handlers._on_joyaxis_motion(joystick, "+joyhat_y", +hat_y)
        joystick_handlers._on_joyaxis_motion(joystick, "-joyhat_y", -hat_y)

    def _on_joyaxis_motion(self, joystick, axis, value):
        key = axis
        value = (value * (1+JOYSTICK_DEADZONE)) - JOYSTICK_DEADZONE
        value = int(max(0, value) * 255) # map value to byte (0 .. 255)
        joystick.states[key] = value
        self.window.send_input_change(("joystick",key))

class Window(pyglet.window.Window):

    def __init__(self, client = None, *args, **kwargs):
        # The crosshairs at the center of the screen.
        self.reticle = None
        # (has to be called before standart init which sometimes calls on_resize)

#        display = pyglet.canvas.get_display()
#        screen = display.get_default_screen()
#
#        template = pyglet.gl.Config(depth_size=8)
#        template.major_version = 3
#        config = screen.get_best_config(template)
#        context = config.create_context(None)
#        kwargs.setdefault("context",context)

        pyglet.window.Window.__init__(self,*args, **kwargs)
        #super(Window, self).__init__(*args, **kwargs)

        # Whether or not the window exclusively captures the mouse and other status info
        self.exclusive = False
        self.hud_open = False
        self.debug_info_visible = False
        self.chat_open = False
        self.chat_input_buffer = ""
        self.chat_cursor_position = 0
        self.hud_replaced_exclusive = False

        glEnable(GL_NORMALIZE)
        self.reload_shaders()
        self.active_shader_is = [0,0]
        self.active_shader_ii = 0

        # Current (x, y, z) position in the world, specified with floats. Note
        # that, perhaps unlike in math class, the y-axis is the vertical axis.
        self.player_position = Vector((0, 0, 0))

        # First element is rotation of the player in the x-z plane (ground
        # plane) measured from the z-axis down. The second is the rotation
        # angle from the ground plane up. Rotation is in degrees.
        #
        # The vertical plane rotation ranges from -90 (looking straight down) to
        # 90 (looking straight up). The horizontal rotation range is unbounded.
        self.player_rotation = (0, 0)

        # And the same for the camera
        self.camera_position = Vector((0, 0, 0))
        self.camera_rotation = (0, 0)
        self.camera_distance = 0 # 0 = first person
        self.camera_smoothing = INITIAL_CAMERA_SMOOTHING
        
        self.d_yaw_player_camera = 0
        
        # Instance of the model that handles the world.
        self.model = Model(chunk_priority_callback=self.distance_to_chunk)
        
        # The label for debug info
        self.label = pyglet.text.Label('', font_name='Arial', font_size=18,
            x=10, y=self.height - 10, anchor_x='left', anchor_y='top',
            color=(0, 0, 0, 255), group=textgroup)

        # The label for current chat_input_buffer
        self.chat_label = pyglet.text.Label('', font_name='Arial', font_size=18,
            x=10, y= 10, anchor_x='left', anchor_y='bottom',
            color=(0, 0, 0, 255), group=textgroup)

        # This call schedules the `update()` method to be called
        # TICKS_PER_SEC. This is the main game event loop.
        pyglet.clock.schedule_interval(self.update, 1.0 / TICKS_PER_SEC)
        self.update_lock = threading.Lock() #make sure there is only 1 update function per time

        # key handler for convinient polling
        self.keystates = key.KeyStateHandler()
        self.push_handlers(self.keystates)
        # and just a variable for the mouse that is updated by event_handlers below
        self.mousestates = collections.defaultdict(bool)
        self.focused_on_mouse_press = None

        # mouse pointer
        self._pointer_position = (0, 0)
        self.pointer_direction = Vector(0, 0, -1)
        self.pointer_position_3d = Vector(0, 0, -1)

        # joysticks
        self.joysticks = pyglet.input.get_joysticks()
        for joystick in self.joysticks:
            joystick.open()
            joystick_handler = JoystickHandler(self)
            joystick.states = collections.defaultdict(int)
            joystick.push_handlers(joystick_handler)

        # current state of actions
        self.actionstates = collections.defaultdict(int)

        # Sound
        self.listener = pyglet.media.get_audio_driver().get_listener()

        # some function to tell about events
        if not client:
            raise ValueError("There must be some client")
        self.client = client

    def reload_shaders(self):
        FRAGMENT_SHADERS = dict() # {name: source_code_bytes, ...}
        shaders_dir = os.path.join(PATH,"shaders")
        for filename in os.listdir(shaders_dir):
            shadername, extension = os.path.splitext(filename)
            if extension == ".frag":
                path = os.path.join(shaders_dir,filename)
                with open(path, "rb")  as f:
                    FRAGMENT_SHADERS[shadername] = f.read()

        self.block_shader_names = sorted(FRAGMENT_SHADERS)
        self.block_shaders = tuple(
                Shader([vertex_shader_code], [FRAGMENT_SHADERS[name]])
            for name in self.block_shader_names
        )


    def on_close(self):
        pyglet.clock.unschedule(self.update)
        super(Window,self).on_close()

    def set_exclusive_mouse(self, exclusive):
        """
        If `exclusive` is True, the game will capture the mouse, if False
        the game will ignore the mouse.
        """
        #pyglet.window.Window.set_exclusive_mouse(self,exclusive)
        super(Window, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive
        self.update_reticle(*self.get_size())

    def distance_to_chunk(self, chunk):
        chunkpos = chunk << CHUNKBASE
        return (self.camera_position - chunkpos).length()

    def get_sight_vector(self, rotation, pitchcorrection=0):
        """
        Returns the current line of sight vector indicating the direction
        the player is looking.
        """
        yaw, pitch = rotation
        pitch += pitchcorrection
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(pitch))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(pitch))
        dx = math.cos(math.radians(yaw - 90)) * m
        dz = math.sin(math.radians(yaw - 90)) * m
        return Vector((dx, dy, dz))

    def update_pointer_direction(self):
        """
        updates the 3D direction corresponding to the current pointer position.
        The length of this vector is not normalized, the forward component is.
        This is to support working with z value from depth buffer to get 3D pointer position.
        """
        front_vector = self.get_sight_vector(self.camera_rotation)
        if self.exclusive:
            self.pointer_direction = front_vector
            return
        front_vector = front_vector.normalize()
        up_vector = self.get_sight_vector(self.camera_rotation, 90).normalize()
        side_vector = front_vector.cross(up_vector)
        
        x, y = self._pointer_position
        w, h = self.get_size()
        f = math.tan(math.radians(FOV/2))/(0.5*h)
        fx = (x-0.5*w) * f
        fy = (y-0.5*h) * f
        self.pointer_direction = front_vector + fx*side_vector + fy*up_vector
    
    def update(self, dt):
        global focus_distance
        with self.update_lock:
            for command, *args in self.client.receive():
                #print("client.py:", c)
                #M# maybe define this function somewhere else
                def test(name,argc):
                    if name == command:
                        if len(args) == argc:
                            return True
                        print("Falsche Anzahl von Argumenten bei %s" %name)
                    return False
                if test("clear",1):
                    generator_data, = args
                    self.model._clear(generator_data)
                elif test("del",1):
                    position, = args
                    position = Vector(position)
                    self.model.remove_block(position)
                elif test("delarea",2):
                    lower_bounds, upper_bounds = args
                    lower_bounds = Vector(lower_bounds)
                    upper_bounds = Vector(upper_bounds)
                    area = Box(lower_bounds, upper_bounds)
                    raise NotImplementedError()
                    #self.model.del_area(position)
                elif test("set", 2):
                    position, block_name = args
                    position = Vector(position)
                    assert type(block_name) == str
                    self.model.add_block(position,block_name)
                elif test("goto",1):
                    position, = args
                    self.player_position = Vector(position)
                elif test("focusdist",1):
                    focus_distance, = args
                    assert isinstance(focus_distance, (int, float))
                elif test("setentity",5):
                    entity_id, model, position, rotation, modelmaps = args
                    assert type(entity_id) == int or print(entity_id)
                    assert isinstance(model, (str, type(None))) or print(model)
                    position = Vector(position)
                    rotation = Vector(rotation)
                    self.model.set_entity(entity_id,model,position,rotation, modelmaps)
                elif test("delentity",1):
                    entity_id, = args
                    self.model.del_entity(entity_id)
                elif test("sethud",6):
                    element_id, texture, position, rotation, size, align = args
                    assert type(element_id) == str
                    assert type(texture) == str
                    position = Vector(position)
                    rotation = float(rotation)
                    size = Vector(size)
                    assert type(align) == int
                    element_data = element_id,texture,position,rotation,size,align
                    self.model.set_hud(element_data,self.get_size()) #id,texture,position,rotation,size,align
                elif test("delhud",1):
                    element_id, = args
                    self.model.del_hud(element_id)
                elif test("focushud",0):
                    self.open_hud()
                elif test("error",2):
                    errmsg, is_fatal = args
                    err = Exception(errmsg)
                    if is_fatal:
                        raise err
                    else:
                        warnings.warn(err)
                elif test("sound",2):
                    sound_name, position = args
                    assert type(sound_name) == str
                    position = Vector(position)
                    self.play_sound(sound_name, position)
                else:
                    print("unknown command", command, args)
            self.model.process_queue()
            m = max(0, MSGS_PER_TICK - len(self.model.queue))
            self.client.send(("tick",m))
            
            dyaw   = self.actionstates["+yaw"]   - self.actionstates["-yaw"]
            dpitch = self.actionstates["+pitch"] - self.actionstates["-pitch"]
            if dyaw != 0 or dpitch != 0:
                k = 0.5
                self.rotate(dyaw*k*dt, dpitch*k*dt)
            
            self.update_player_rotation()
            self.update_camera_position()

    def update_player_rotation(self):
        previous_rotation = self.player_rotation
        
        dx, dy, dz = self.pointer_position_3d - self.player_position
        lxz = Vector(dx,dz).length()
        if lxz:
            pitch = math.degrees(math.atan(dy/lxz))
            yaw = math.degrees(math.atan2(dz, dx))+90 if lxz else self.camera_rotation[0]
        else:
            print("could not determine player rotation")
            return
        
        if (yaw, pitch) != previous_rotation:
            self.player_rotation = (yaw, pitch)
            self.client.send(("rot", self.player_rotation))
        
        d_yaw = self.player_rotation[0] - self.camera_rotation[0]
        if d_yaw != self.d_yaw_player_camera:
            self.d_yaw_player_camera = d_yaw
            if any(self.actionstates[d] for d in ("for","back","left","right")):
                self.send_input_change(True)
    
    def update_camera_position(self):
        # eye offset
        AH = 0.32
        yaw, pitch = self.camera_rotation
        c = math.cos(math.radians(yaw))
        s = math.sin(math.radians(yaw))
        dx = AH* math.sin(math.radians(pitch))*-s
        dz = AH* math.sin(math.radians(pitch))*c
        dy = AH*(math.cos(math.radians(pitch))-1)
        eye_position = self.player_position + (dx,dy,dz)
        # third person
        camera_position_target = eye_position - self.get_sight_vector(self.camera_rotation)*self.camera_distance
        # smooth camera
        self.camera_position = self.camera_smoothing*self.camera_position + (1-self.camera_smoothing)*camera_position_target

        # audio
        self.listener.position = tuple(self.camera_position)
        # monitored area
        for msg in self.model.monitor_around(self.camera_position):
            self.client.send(msg)
    
    def update_pointer_position_3d(self):
        # has to be called after world but before hud draw calls

        # update pointer vector
        self.update_pointer_direction()
        
        # read out pixel depth from framebuffer
        x, y = self._pointer_position
        depth = ctypes.c_float()
        glReadPixels( x, y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT, ctypes.cast(ctypes.addressof(depth), ctypes.c_void_p))
        clip_z = (depth.value - 0.5) * 2.0
        d = -2*ZFAR*ZNEAR/(clip_z*(ZFAR-ZNEAR)-(ZFAR+ZNEAR))
        d += 0 # offset half a block back to better look at center of block?

        # alternative implementation using raycast on model
        #d = Ray(self.camera_position, pointer_vector).hit_test(lambda pos:self.model.get_block(pos)!="AIR", (max(RENDERDISTANCE)+1)*CHUNKSIZE)[0]
        #d /= pointer_vector.length()

        self.pointer_position_3d = self.camera_position + d * self.pointer_direction

    def open_hud(self):
        self.hud_open = True
        self.hud_replaced_exclusive = self.exclusive
        self.set_exclusive_mouse(False)

    def close_hud(self):
        self.hud_open = False
        if self.hud_replaced_exclusive:
            self.set_exclusive_mouse(True)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        #self.client.send(("scrolling",scroll_y))
        symbol_x = "right" if scroll_x>0 else "left"
        symbol_y = "up"    if scroll_y>0 else "down"
        #print(symbol_x, symbol_y, KEYMAP)
        for e, action in KEYMAP:
            e_type, symbol = e
            if e_type == "scroll":
                if symbol == symbol_x:
                    for _ in range(math.ceil(abs(scroll_x))):
                        self.client.send(("press",action))
                if symbol == symbol_y:
                    for _ in range(math.ceil(abs(scroll_y))):
                        self.client.send(("press",action))
        
    def get_focused(self, x, y):
        focused = None
        z = float("-inf")
        for _,element_data,(center, (c,s), size) in self.model.hud_elements.values():
            name = element_data[0]
            if name.startswith("#"):
                dx, dy = x - center[0], y - center[1]
                drx, dry = c*dx + s*dy, c*dy - s*dx
                if abs(drx) < 0.5*size[0] and abs(dry) < 0.5*size[1]:
                    if center[2] > z:
                        focused = name
                        z = center[2]
        return focused

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called when a mouse button is pressed. See pyglet docs for button
        amd modifier mappings.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        button : int
            Number representing mouse button that was clicked. 1 = left button,
            4 = right button.
        modifiers : int
            Number representing any modifying keys that were pressed when the
            mouse button was clicked.
        """
        if not self.exclusive:
            self.focused_on_mouse_press = self.get_focused(x,y)
            if self.focused_on_mouse_press != None:
                return
            #if self.hud_open:
            #    self.client.send(("press","inv"))
            #    self.close_hud()
            #    return
            w,h = self.get_size()
            if (x-0.5*w)**2 + (y-0.5*h)**2 <= 50**2:
                self.set_exclusive_mouse(True)
                return
            # drop through to sending mouse event to server
        self.mousestates[button] = True
        self.send_input_change(("mouse",button))
    
    def on_mouse_release(self, x, y, button, modifiers):
        self.mousestates[button] = False
        self.send_input_change(("mouse",button))
        
        if not self.exclusive:
            if (button == mouse.RIGHT) or \
                ((button == mouse.LEFT) and (modifiers & key.MOD_CTRL)):
                # ON OSX, control + left click = right click.
                button_name = "right"
            elif button == pyglet.window.mouse.LEFT:
                button_name = "left"
            else:
                button_name = None
            if button_name:
                focused_on_mouse_release = self.get_focused(x,y)
                if self.focused_on_mouse_press == focused_on_mouse_release:
                    self.client.send(("clicked",button_name,
                                      self.focused_on_mouse_press))
                else:
                    self.client.send(("dragged",button_name,
                                      self.focused_on_mouse_press, focused_on_mouse_release))
            self.focused_on_mouse_press = None
    
    def on_mouse_leave(self, x, y):
        self.mousestates.clear()
        self.send_input_change(True)

    def rotate(self, dyaw, dpitch):
        yaw, pitch = self.camera_rotation
        yaw += dyaw
        pitch += dpitch
        pitch = max(-90, min(90, pitch))
        self.camera_rotation = (yaw,pitch)

        self.listener.forward_orientation = tuple(self.get_sight_vector(self.camera_rotation))
        self.listener.up_orientation = tuple(self.get_sight_vector(self.camera_rotation,90))
    
    def on_mouse_motion(self, x, y, dx, dy):
        """
        Called when the player moves the mouse.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse. Always center of the screen if
            the mouse is captured.
        dx, dy : float
            The movement of the mouse.
        """
        if self.exclusive:
            m = 0.15
            self.rotate(dx*m, dy*m)
            w,h = self.get_size()
            self._pointer_position = w//2, h//2
        else:
            self._pointer_position = x, y

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.on_mouse_motion(x, y, dx, dy)

    def send_input_change(self, event):
        used_events = set([i[0] for i in KEYMAP])
        if (event in used_events) or (event == True):
            self.actionstates.clear()
            for e, action in KEYMAP:
                (event_type, symbol) = e
                value = 0
                if (event_type == "key"   and self.keystates[symbol] and not self.chat_open):
                    value = 255
                if (event_type == "mouse" and self.mousestates[symbol]):
                    value = 255
                if (event_type == "joystick"):
                    for joystick in self.joysticks:
                        value = max(value, joystick.states[symbol])
                if event == e:
                    self.handle_input_action(action, value)
                self.actionstates[action] = max(value, self.actionstates[action])
            dx = self.actionstates["right"] - self.actionstates["left"]
            dz = self.actionstates["back"] - self.actionstates["for"]
            da = math.radians(self.d_yaw_player_camera)
            c, s = math.cos(da), math.sin(da)
            dx, dz = dx*c + dz*s, dz*c - dx*s
            self.actionstates["right"] = max(0, min(255, int(round(+dx))))
            self.actionstates["left"]  = max(0, min(255, int(round(-dx))))
            self.actionstates["back"]  = max(0, min(255, int(round(+dz))))
            self.actionstates["for"]   = max(0, min(255, int(round(-dz))))
            actionstates = bytearray(self.actionstates[a] for a in ACTIONS)
            actionstates_b64 = base64.encodebytes(actionstates.rstrip(b"\00")).decode("ascii")
            self.client.send(("keys",actionstates_b64))

    def handle_input_action(self, action, value):
        if action == "inv" and value > 0:
            if self.hud_open:
                self.close_hud()
        if action == "chat" and value == 0: #do this on release, so key is not printed into chat
            self.chat_open = True

    def on_key_press(self, symbol, modifiers):
        """
        Called when the player presses a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.
        """

        if symbol == key.ESCAPE:
            if self.chat_open:
                self.client.send(("press","chat_close"))
                self.chat_open = False
            else:
                self.hud_replaced_exclusive = False
                self.set_exclusive_mouse(False)
        else:
            if symbol == key.F3:
                self.debug_info_visible = not self.debug_info_visible
            if symbol == key.F4:
                self.active_shader_is[self.active_shader_ii] += -1 if modifiers & key.MOD_SHIFT else 1
                self.active_shader_is[self.active_shader_ii] %= len(self.block_shaders)
            if symbol == key.F5:
                self.active_shader_ii += -1 if modifiers & key.MOD_SHIFT else 1
                self.active_shader_ii %= len(self.active_shader_is)
            if symbol == key.F6:
                self.camera_distance = 10 - self.camera_distance
            if symbol == key.F7:
                ds = -0.1 if modifiers & key.MOD_SHIFT else +0.1
                self.camera_smoothing = max(0,min(0.99, self.camera_smoothing+ds))
            if symbol == key.F9:
                self.reload_shaders()
            if symbol == key.F11:
                self.set_fullscreen(not self.fullscreen)
            if self.chat_open:
                pass
            self.send_input_change(("key", symbol))
                
    def on_key_release(self, symbol, modifiers):
        self.send_input_change(("key", symbol))

    def on_text(self, text):
        if self.chat_open:
            for c in text:
                if c in ("\n","\r"):
                    self.client.send(("text",self.chat_input_buffer))
                    self.chat_input_buffer = ""
                    self.chat_cursor_position = 0
                else:
                    self.chat_input_buffer = (
                        self.chat_input_buffer[:self.chat_cursor_position] + 
                        c +
                        self.chat_input_buffer[self.chat_cursor_position:] )
                    self.chat_cursor_position += 1
    
    def on_text_motion(self, motion):
        """The user moved the text input cursor.
        """
        if not self.chat_open:
            return
        
        l = len(self.chat_input_buffer)

        if motion == key.MOTION_BACKSPACE:
            self.chat_input_buffer = (self.chat_input_buffer[:self.chat_cursor_position-1] + 
                                      self.chat_input_buffer[self.chat_cursor_position:] )
            self.chat_cursor_position -= 1
        elif motion == key.MOTION_DELETE:
            self.chat_input_buffer = (self.chat_input_buffer[:self.chat_cursor_position] + 
                                      self.chat_input_buffer[self.chat_cursor_position+1:] )
        elif motion == key.MOTION_LEFT:
            self.chat_cursor_position -= 1
        elif motion == key.MOTION_RIGHT:
            self.chat_cursor_position += 1
        elif motion in (key.MOTION_BEGINNING_OF_LINE, key.MOTION_PREVIOUS_PAGE, key.MOTION_BEGINNING_OF_FILE):
            self.chat_cursor_position = 0
        elif motion in (key.MOTION_END_OF_LINE, key.MOTION_NEXT_PAGE, key.MOTION_END_OF_FILE):
            self.chat_cursor_position = l
        elif motion == key.MOTION_UP:
            print("chat history is not implemented yet")
        elif motion == key.MOTION_DOWN:
            print("chat history is not implemented yet")
        elif motion == key.MOTION_NEXT_WORD:
            print("moving cursor to next word is not implemented yet")
        elif motion == key.MOTION_PREVIOUS_WORD:
            print("moving cursor to previous word is not implemented yet")
        else:
            print("encountered unknown text motion", motion)

        self.chat_cursor_position = max(0, min(l, self.chat_cursor_position))


    def on_resize(self, width, height):
        """
        Called when the window is resized to a new `width` and `height`.
        """
        # label
        self.label.y = height - 10
        # reticle
        self.update_reticle(width, height)
        # hud
        self.model.hud_resize(self.get_size())
    
    def update_reticle(self, width, height):
        if self.reticle:
            self.reticle.delete()
        x, y = self.width / 2, self.height / 2
        if self.exclusive or self.hud_replaced_exclusive:
            n = 10
            lines = [((-n, 0), (n, 0)),
                     ((0, -n), (0, n))]
        else:
            n = 50
            points = [(n*math.cos(math.radians(a)),n*math.sin(math.radians(a)))
                      for a in range(0, 360, 10)]
            lines = [(points[i],points[(i+1)%len(points)]) for i in range(len(points))]
        centered_lines = tuple((p + dp)
                               for line in lines
                               for point in line
                               for p, dp in zip((x,y), point))
        self.reticle = pyglet.graphics.vertex_list(len(centered_lines)//2,
            ('v2f', centered_lines)
        )

    def set_2d(self):
        """
        Configure OpenGL to draw in 2d.
        """
        width, height = self.get_size()
        #glDisable(GL_DEPTH_TEST)
        glClear(GL_DEPTH_BUFFER_BIT)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_3d(self):
        """
        Configure OpenGL to draw in 3d.
        """
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(FOV, width / float(height), ZNEAR, ZFAR)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        yaw, pitch = self.camera_rotation
        c = math.cos(math.radians(yaw))
        s = math.sin(math.radians(yaw))
        glRotatef(yaw, 0, 1, 0)
        glRotatef(-pitch, c, 0, s)
        x, y, z = self.camera_position
        glTranslatef(-x, -y, -z)

    def on_draw(self):
        """
        Called by pyglet to draw the canvas.
        """
        r,g,b,a = self.model.world_generator.sky(self.camera_position, time.time()) if hasattr(self.model,"world_generator") else (1,1,1,1)
        glClearColor(r,g,b,a) # Set the color of "clear", i.e. the sky, in rgba.
        self.clear()
        fog_color = get_fog(self.model.get_block(self.camera_position.round()))
        setup_fog(fog_color)
        self.set_3d()
        glColor3d(1, 1, 1)
        block_shader = self.block_shaders[self.active_shader_is[self.active_shader_ii]]
        block_shader.bind()
        self.model.batch.draw()
        block_shader.unbind()
        
        self.update_pointer_position_3d()
        
        x = 0.25 #1/(Potenzen von 2) sind sinnvoll, je größer der Wert, desto stärker der Kontrast
        glColor3d(x, x, x)
        glEnable(GL_COLOR_LOGIC_OP)
        glLogicOp(GL_XOR)

        self.draw_focused_block()
        self.set_2d()
        self.draw_reticle()

        glClear(GL_DEPTH_BUFFER_BIT)
        glDisable(GL_COLOR_LOGIC_OP)
        glColor3d(1, 1, 1)
        self.model.hud_batch.draw()
        
        if self.debug_info_visible:
            self.draw_debug_info()
        if self.chat_open:
            self.draw_chat_buffer()
    
    def draw_debug_info(self):
        """
        draw stuff like Position, Rotation, FPS, ...
        """
        x, y, z = self.player_position
        fps = pyglet.clock.get_fps()
        queue = len(self.model.queue)
        face_buffer = len(self.model.blockface_update_buffer)
        terrain_queue = len(self.model.init_chunk_queue.chunks)
        shader_names = "".join(
            ("[%s]" if self.active_shader_ii==ii else " %s ") % self.block_shader_names[i]
            for ii,i in enumerate(self.active_shader_is)
        )
        
        self.label.text = 'FPS: %03d \t Position: (%.2f, %.2f, %.2f) \t Buffer: %04d, %04d, %04d \t cd[F6]:%.1f cs[F7]:%.2f \t [F4/F5]: %s' % (fps, x, y, z, queue, face_buffer, terrain_queue, self.camera_distance, self.camera_smoothing, shader_names)
        self.label.draw()
    
    def draw_chat_buffer(self):
        """
        draw the text the user is currently entering into chat (not send to server yet)
        """
        show_cursor = (int(time.time()*1.5)&1) #and (self.chat_cursor_position != len(self.chat_input_buffer))
        caret = "|" if show_cursor else " "
        self.chat_label.text = (self.chat_input_buffer[:self.chat_cursor_position] + caret +
                                self.chat_input_buffer[self.chat_cursor_position:] )
        self.chat_label.draw()

    def draw_focused_block(self):
        """
        Draw black edges around the block that is currently under the
        crosshairs.
        """
        vector = self.get_sight_vector(self.player_rotation)
        if CHUNKSIZE == None:
            return
        block = Ray(self.player_position, vector).hit_test(lambda pos:self.model.get_block(pos)!="AIR", focus_distance)[1]
        if block:
            x, y, z = block
            vertex_data = cube_vertices(x, y, z, 0.51)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            pyglet.graphics.draw(24, GL_QUADS, ('v3f/static', vertex_data))
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def draw_reticle(self):
        """
        Draw the crosshairs in the center of the screen.
        """
        self.reticle.draw(GL_LINES)

    def play_sound(self, sound_name, position):
        if sound_name in SOUNDS:
            player = SOUNDS[sound_name].play()
            player.position = position
        else:
            print("unknown sound name", sound_name)

def setup_fog(fog_color):
    """
    Configure the OpenGL fog properties.
    """
    # Enable fog. Fog "blends a fog color with each rasterized pixel fragment's
    # post-texturing color."
    #glEnable(GL_FOG)
    # Set the fog color.
    glFogfv(GL_FOG_COLOR, (GLfloat * 4)(*(c/255 for c in fog_color)))
    # Say we have no preference between rendering speed and quality.
    #glHint(GL_FOG_HINT, GL_DONT_CARE)
    # Specify the equation used to compute the blending factor.
    #glFogi(GL_FOG_MODE, GL_LINEAR)
    # How close and far away fog starts and ends. The closer the start and end,
    # the denser the fog in the fog range.
    #glFogf(GL_FOG_START, 0.0)
    #glFogf(GL_FOG_END, 3.0)

def setup():
    """ Basic OpenGL configuration.

    """
    # Enable culling (not rendering) of back-facing facets -- facets that aren't
    # visible to you.
    glEnable(GL_CULL_FACE)

    # Set the texture minification/magnification function to GL_NEAREST (nearest
    # in Manhattan distance) to the specified texture coordinates. GL_NEAREST
    # "is generally faster than GL_LINEAR, but it can produce textured images
    # with sharper edges because the transition between texture elements is not
    # as smooth."
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    #setup_fog()

def show_on_window(client):
    window = None
    try:
        if args.name:
            entity_id = args.name
            password = args.password
        else:
            entity_id = "tmp:" + hex(random.getrandbits(32))[2:]
            password = hex(random.getrandbits(32))[2:]
            if args.password:
                print("Ignoring user set password because no name was given.")
        client.send(("control", entity_id, password))
        window = Window(width=800, height=600, caption='MCG-Craft 1.1.4',
                        resizable=True, client=client, fullscreen=False)
        # Hide the mouse cursor and prevent the mouse from leaving the window.
        window.set_exclusive_mouse(True)
        setup()
        pyglet.app.run()
    except Exception as e:
        raise
        if e.message != "Disconnect" and e.message != "Server went down.":
            raise
        else:
            print(e.message)
    finally:
        if window:
            window.on_close()
    
def run(serverinfo):
    load_setup(serverinfo["host"], serverinfo["http_port"])
    addr = (serverinfo["host"], serverinfo["game_port"])
    try:
        with socket_connection.client(addr) as socket_client:
            show_on_window(socket_client)
    except socket_connection.Disconnect:
        print("Client closed due to disconnect.")

def main():
    serverinfo = client_utils.get_serverinfo(args)
    if serverinfo:
        run(serverinfo)

args = client_utils.parser.parse_args()
if __name__ == '__main__':
    main()
