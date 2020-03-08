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
import json
import urllib.request
import io

# Adding directory with modules to python path
PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(os.path.join(PATH,"..","..","modules"))
sys.path.append(os.path.join(PATH,"..","..",".."))

import pyglet
from pyglet import image
#pyglet.options["debug_gl"] = False
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse

import socket_connection_4.socket_connection_4 as socket_connection
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

focus_distance = 0

# Mapping of keys to events
KEYMAP = [
    (key._1    ,"inv1"  ),
    (key._2    ,"inv2"  ),
    (key._3    ,"inv3"  ),
    (key._4    ,"inv4"  ),
    (key._5    ,"inv5"  ),
    (key._6    ,"inv6"  ),
    (key._7    ,"inv7"  ),
    (key._8    ,"inv8"  ),
    (key._9    ,"inv9"  ),
    (key._0    ,"inv0"  ),
    (key.W     ,"for"   ),
    (key.S     ,"back"  ),
    (key.A     ,"left"  ),
    (key.D     ,"right" ),
    (key.SPACE ,"jump"  ),
    (key.TAB   ,"fly"   ),
    (key.E     ,"inv"   ),
    (key.LSHIFT,"shift" ),
    (key.LCTRL ,"sprint"),
    ]
import appdirs
configdir = appdirs.user_config_dir("MCGCraft","ProgrammierAG")
configfn = os.path.join(configdir,"clientsettings.py")
print(configfn)
if os.path.exists(configfn):
    with open(configfn) as configfile:
        config = eval(configfile.read(),globals())
        if "controls" in config:
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

vertex_shader_code = """
#version 330

varying out vec3 color;

void main()
{
    //normal = gl_NormalMatrix * gl_Normal;
    color = gl_Color;
    gl_Position = ftransform();
    gl_TexCoord[0] = gl_MultiTexCoord0;
}
"""

fancy_fragment_shader_code = """
#version 330

varying in vec3 color;
uniform sampler2D color_texture;

void main (void)
{
    vec4 tex_color = texture2D(color_texture, gl_TexCoord[0].st);
    //float test = dot(normal, vec3(0.0f,1.0f,0.0f));
    gl_FragColor = tex_color * (0.5 + 0.5 * vec4(color, 0));
}
"""

plain_fragment_shader_code = """
#version 330

varying in vec3 color;
uniform sampler2D color_texture;

void main (void)
{
    gl_FragColor = texture2D(color_texture, gl_TexCoord[0].st);
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
    global BLOCKMODELS, TRANSPARENCY, TEXTURE_DIMENSIONS, TEXTURE_URL, TEXTURE_EDGE_CUTTING, ENTITY_MODELS, ICON, BLOCKNAMES
    def url_for(filename):
        path = os.path.join("/texturepacks/desktop",filename)
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
    ICON = collections.defaultdict(lambda:ICON["missing_texture"])
    BLOCKMODELS = BlockModelDict()
    BLOCKNAMES = []
    for name, transparency, icon_index, textures in description["BLOCKS"]:
        n = 0.5 - 0.01*transparency
        if not transparency:
            BLOCKNAMES.append(name)
        BLOCKMODELS[name] = cube_model(textures,n,not transparency) #[top,bottom,front,back,left,right[,other]] = [(vertices,tex_coords),...]
        ICON[name] = tex_coord(*textures[icon_index])
        TRANSPARENCY[name] = transparency
    for name, transparency, icon_coords, vertices, textures in description["BLOCK_MODELS"]:
        BLOCKMODELS[name] = block_model(vertices, textures)
        ICON[name] = tex_coord(*icon_coords)
        TRANSPARENCY[name] = transparency

def is_transparent(block_name):
    return TRANSPARENCY.get(block_name.rsplit(":",1)[0],0)

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
    def __init__(self):
        self.chunks = collections.OrderedDict()
        self.current_chunk = None
        self.positions = None
        self.current_position = None
    def _refill(self):
        if self.chunks:
            self.current_chunk = self.chunks.popitem(last=False)[0]
            self.positions = iterchunk()
            self.current_position = next(self.positions)
        else:
            self.current_chunk = None
    def add(self, value):
        self.chunks[value] = None
        if not self.current_chunk:
            self._refill()
    def is_empty(self):
        return self.current_chunk == None
    def pop(self):
        value = (self.current_chunk << CHUNKBASE) + self.current_position
        try:
            self.current_position = next(self.positions)
        except StopIteration:
            self._refill()
        return value

class Model(object):

    def __init__(self):

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
        self.init_chunk_queue = InitChunkQueue()

        self.occlusion_cache = collections.OrderedDict()

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
        #print(generator_data)
        self.world_generator = world_generation.WorldGenerator(generator_data, init_py = False)
        self.blocks.set_terrain_function(self.world_generator.terrain)

    def monitor_around(self, position):
        """returns list of messages to be send to client in order to announce new monitoring area and required updates"""
        if not hasattr(self, "world_generator"):
            print("received goto before clear, fix message_buffer asap!")
            self.monitor_after_clear = True
            return
        center_chunk_position = position.round() >> CHUNKBASE
        added, removed = self.chunks.monitor_around(center_chunk_position)
        
        added_chunks_with_areas_and_mid = [(chunkpos,
                                            BinaryBox(CHUNKBASE, chunkpos).bounding_box(),
                                            self.chunks.unmonitored_since_ids[chunkpos])
                                           for chunkpos in added]
        #sort added by distance to position
        added_chunks_with_areas_and_mid.sort(key = lambda x, p=Point(position): x[1].distance(p))

        for chunkpos, area, m_id in added_chunks_with_areas_and_mid:
            # update visibility of blocks in chunks (show blocks from terrain function)
            if m_id == 0:
                if self.world_generator.terrain_hint((CHUNKBASE,chunkpos),"visible"):
                    self.init_chunk_queue.add(chunkpos)

            # create messages for server
            yield "update %s %i" % (area, m_id)
        lowest_corner_chunk = center_chunk_position - RENDERDISTANCE
        highest_corner_chunk = center_chunk_position + RENDERDISTANCE
        x1, y1, z1 = lowest_corner_chunk << CHUNKBASE
        x2, y2, z2 = ((highest_corner_chunk + (1,1,1)) << CHUNKBASE) - (1,1,1)
        yield "monitor %i %i %i %i %i %i %i" % (x1,y1,z1, x2,y2,z2, self.chunks.current_monitor_id)


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
            cc = self.ambient_occlusion(vertex) + self.sunlight(vertex, face)
            cc = (0.5 + 0.5 * cc)
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
            # only show faces facing into transparent blocks and not if blocks are the same
            if is_transparent(b) and b != self.get_block(position): #M# maybe get current block as argument instead of by position
                self.show_face(position,face)
            else:
                self.hide_face(position,face)
            
    def update_visibility_around(self,position):
        #M# make better!
        for x in (-1,0,1):
            for y in (-1,0,1):
                for z in (-1,0,1):
                    v = Vector((x,y,z)) + position
                    if v != (0,0,0):
                        self.update_visibility(v)

        #original:
        #for f,fv in enumerate(FACES):
        #    self.update_face(position+fv,(f+1-(2*(f%2))))
    
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

    def set_entity(self,entity_id,model_id,position,rotation):
        self.del_entity(entity_id)
        if model_id == "0":
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
            for relpos,offset,size,texture in model[modelpart]:
                x, y, z = offset if modelpart in ("head","legl","legr") else relpos
                if texture == "<<random>>":
                    texture = BLOCKNAMES[entity_id%len(BLOCKNAMES)] #make sure to select from list that doesn't change, cause otherwise players skins will change
                blockmodel = BLOCKMODELS[texture] # using blockmodels here seems strange :(
                for face in range(len(FACES)):
                    texture_data = blockmodel[face][1]
                    vertex_data = face_vertices_noncube(x, y, z, face, (i/2.0 for i in size))
                    if modelpart == "head":
                        vertex_data = self._transform(head_matrix,relpos,vertex_data)
                    if modelpart == "legl":
                        vertex_data = self._transform(legl_matrix,relpos,vertex_data)
                    if modelpart == "legr":
                        vertex_data = self._transform(legr_matrix,relpos,vertex_data)
                    vertex_data = self._transform(body_matrix,position,vertex_data)
                    # create vertex list
                    # FIXME Maybe `add_indexed()` should be used instead
                    vertex_lists.append(self.batch.add(4, GL_QUADS, self.textured_normal_group,
                        ('v3f/static', vertex_data),
                        ('t2f/static', texture_data)))
                    #M# make only one vertex list per entity!
        self.entities[entity_id] = vertex_lists

    def del_entity(self,entity_id):
        vertex_lists = self.entities.pop(entity_id,[])
        for vertex_list in vertex_lists:
            vertex_list.delete()

    def set_hud(self,element_data,window_size):#id,texture,position,rotation,size,align
        element_id,texture,position,rotation,size,align = element_data
        if element_id in self.hud_elements:
            self.del_hud(element_id)
        if texture == "AIR":
            return
        f = (max if OUTER & align else min)(window_size)
        size = f*Vector(size)
        center_pos = tuple(((1+bool(align & pa)-bool(align & na))*(ws-f) + (xy+1)*f) / 2
                            for pa,na,ws,xy,si in zip((RIGHT,TOP),(LEFT,BOTTOM),window_size,position,size)
                            )
        corners = tuple(xy + (k*si / 2)
                        for ks in ((-1,-1),(1,-1),(1,1),(-1,1))
                        for xy, si, k in zip(center_pos,size,ks)
                        )
        i = iter(corners)
        corners = [a for b in zip(i,i,(position[2],)*4) for a in b]
        #img = pygame.transform.rotate(img,rotation)
        if not texture.startswith ("/"):
            texture_data = list(ICON[texture])
            vertex_list = self.hud_batch.add(4, GL_QUADS, self.textured_colorkey_group,
                            ('v3f/static', corners),
                            ('t2f/static', texture_data))
        else:
            x,y = center_pos
            label = pyglet.text.Label(texture[1:],x=x,y=y,
                                      anchor_x='center',anchor_y='center',
                                      batch=self.hud_batch,group=textgroup,
                                      font_name="Arial")
            vertex_list = label #of course the label isn't simply a vertex list, but it has a delete method, so it should work
        self.hud_elements[element_id] = (vertex_list,element_data,corners)
        
    def del_hud(self,element_id):
        vertex_list = self.hud_elements.pop(element_id,[None])[0]
        if vertex_list:
            vertex_list.delete()

    def hud_resize(self, window_size):
        for vertex_list,element_data,_ in self.hud_elements.values():
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

class Window(pyglet.window.Window):

    def __init__(self, client = None, *args, **kwargs):
        # The crosshairs at the center of the screen.
        self.reticle = None
        # (has to be called before standart init which sometimes calls on_resize)

        pyglet.window.Window.__init__(self,*args, **kwargs)
        #super(Window, self).__init__(*args, **kwargs)

        # Whether or not the window exclusively captures the mouse.
        self.exclusive = False
        self.hud_open = False
        self.debug_info_visible = False

        #self.block_shaders = [fancy_block_shader, plain_block_shader]

        # Current (x, y, z) position in the world, specified with floats. Note
        # that, perhaps unlike in math class, the y-axis is the vertical axis.
        self.position = Vector((0, 0, 0))

        # First element is rotation of the player in the x-z plane (ground
        # plane) measured from the z-axis down. The second is the rotation
        # angle from the ground plane up. Rotation is in degrees.
        #
        # The vertical plane rotation ranges from -90 (looking straight down) to
        # 90 (looking straight up). The horizontal rotation range is unbounded.
        self.rotation = (0, 0)

        # Instance of the model that handles the world.
        self.model = Model()
        
        # The label that is displayed in the top left of the canvas.
        self.label = pyglet.text.Label('', font_name='Arial', font_size=18,
            x=10, y=self.height - 10, anchor_x='left', anchor_y='top',
            color=(0, 0, 0, 255))

        # This call schedules the `update()` method to be called
        # TICKS_PER_SEC. This is the main game event loop.
        pyglet.clock.schedule_interval(self.update, 1.0 / TICKS_PER_SEC)
        self.update_lock = threading.Lock() #make sure there is only 1 update function per time

        # key handler for convinient polling
        self.keystates = key.KeyStateHandler()
        self.push_handlers(self.keystates)

        # some function to tell about events
        if not client:
            raise ValueError("There must be some client")
        self.client = client

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

    def get_sight_vector(self):
        """
        Returns the current line of sight vector indicating the direction
        the player is looking.
        """
        x, y = self.rotation
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return Vector((dx, dy, dz))

    def update(self, dt):
        global focus_distance
        with self.update_lock:
            while True:
                c = self.client.receive()
                if not c:
                    break
                #print("client.py:", c)
                if c.startswith("clear"):
                    generator_data = ast.literal_eval(c[6:])
                    self.model._clear(generator_data)
                    if self.model.monitor_after_clear: #M# this is a hack
                        for msg in self.model.monitor_around(self.position):
                            self.client.send(msg)
                        self.model.monitor_after_clear = False
                    continue
                c = c.split(" ")
                #M# maybe define this function somewhere else
                def test(name,argc):
                    if name == c[0]:
                        if len(c) == argc:
                            return True
                        print("Falsche Anzahl von Argumenten bei %s" %name)
                    return False
                if test("del",4):
                    position = Vector(map(int,c[1:4]))
                    self.model.remove_block(position)
                elif test("delarea",7):
                    x_min, y_min, z_min, x_max, y_max, z_max = map(int, c[1:7])
                    area = Box(Vector(x_min, y_min, z_min), Vector(x_max, y_max, z_max))
                    raise NotImplementedError()
                    position = Vector(map(int,c[1:4]))
                    self.model.del_area(position)
                elif test("set", 5):
                    position = Vector(map(int,c[1:4]))
                    self.model.add_block(position,c[4])
                elif test("goto",4):
                    position = Vector(map(float,c[1:4]))
                    self.position = position
                    for msg in self.model.monitor_around(position):
                        self.client.send(msg)
                elif test("focusdist",2):
                    focus_distance = float(c[1])
                elif test("setentity",8):
                    position = Vector(map(float,c[3:6]))
                    rotation = map(float,c[6:8])
                    self.model.set_entity(int(c[1]),c[2],position,rotation)
                elif test("delentity",2):
                    self.model.del_entity(int(c[1]))
                elif test("sethud",10):
                    position = Vector(map(float,c[3:6]))
                    rotation = float(c[6])
                    size = Vector(map(float,c[7:9]))
                    element_data = c[1],c[2],position,rotation,size,int(c[9])
                    self.model.set_hud(element_data,self.get_size()) #id,texture,position,rotation,size,align
                elif test("delhud",2):
                    self.model.del_hud(c[1])
                elif test("focushud",1):
                    self.set_exclusive_mouse(False)
                    self.hud_open = True
                else:
                    print("unknown command", c)
            self.model.process_queue()
            m = max(0, MSGS_PER_TICK - len(self.model.queue))
            self.client.send("tick %s" % m)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.client.send("scrolling: "+str(scroll_y))
        
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
        if (button == mouse.RIGHT) or \
            ((button == mouse.LEFT) and (modifiers & key.MOD_CTRL)):
            # ON OSX, control + left click = right click.
            event = "right click"
        elif button == pyglet.window.mouse.LEFT:
            event = "left click"
        else:
            return
        if self.exclusive:
            self.client.send(event)
        else:
            focused = None
            z = float("-inf")
            for _,element_data,corners in self.model.hud_elements.values():
                if corners[0] < x < corners[6]:
                    if corners[1] < y < corners[7]:
                        if corners[2] > z:
                            focused = element_data[0]
                            z = corners[2]
            if focused:
                self.client.send(event+"ed "+focused)
            else:
                if self.hud_open:
                    self.client.send("inv")
                    self.hud_open = False
                self.set_exclusive_mouse(True)
                
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
            x, y = self.rotation
            x, y = x + dx * m, y + dy * m
            y = max(-90, min(90, y))
            self.rotation = (x, y)
            self.client.send("rot %s %s" %self.rotation)

    def send_key_change(self, symbol, modifiers, state):
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
        
        used_keys = set([i[0] for i in KEYMAP])
        eventstates = int(bool(modifiers & key.MOD_CTRL))
        if symbol in used_keys:
            for k,e in KEYMAP:
                if self.keystates[k]:
                    eventstates |= 1<<(ACTIONS.index(e)+1)
            self.client.send("keys "+str(eventstates))

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.set_exclusive_mouse(False)
        else:
            if symbol == key.E:
                if self.hud_open:
                    self.hud_open = False
                    self.set_exclusive_mouse(True)
            if symbol == key.F3:
                self.debug_info_visible = not self.debug_info_visible
            if symbol == key.F4:
                self.block_shaders.append(self.block_shaders.pop(0))
            self.send_key_change(symbol, modifiers, True)
                
    def on_key_release(self, symbol, modifiers):
        self.send_key_change(symbol, modifiers, False)

    def on_resize(self, width, height):
        """
        Called when the window is resized to a new `width` and `height`.
        """
        # label
        self.label.y = height - 10
        # reticle
        if self.reticle:
            self.reticle.delete()
        x, y = self.width // 2, self.height // 2
        n = 10
        self.reticle = pyglet.graphics.vertex_list(4,
            ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
        )
        # hud
        self.model.hud_resize(self.get_size())

    def set_2d(self):
        """
        Configure OpenGL to draw in 2d.
        """
        width, height = self.get_size()
        #glDisable(GL_DEPTH_TEST)
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
        gluPerspective(65.0, width / float(height), 0.1, 200.0) #last value is Renderdistance ... was once 60
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        yaw, pitch = self.rotation
        c = math.cos(math.radians(yaw))
        s = math.sin(math.radians(yaw))
        glRotatef(yaw, 0, 1, 0)
        glRotatef(-pitch, c, 0, s)
        AH = 0.32
        dx = AH* math.sin(math.radians(pitch))*-s
        dz = AH* math.sin(math.radians(pitch))*c
        dy = AH*(math.cos(math.radians(pitch))-1)
        x, y, z = self.position
        glTranslatef(-x-dx, -y-dy, -z-dz)

    def on_draw(self):
        """
        Called by pyglet to draw the canvas.
        """
        self.clear()
        self.set_3d()
        glColor3d(1, 1, 1)
        #self.block_shaders[0].bind()
        self.model.batch.draw()
        #self.block_shaders[0].unbind()
        
        x = 0.25 #1/(Potenzen von 2) sind sinnvoll, je größer der Wert, desto stärker der Kontrast
        glColor3d(x, x, x)
        glEnable(GL_COLOR_LOGIC_OP)
        glLogicOp(GL_XOR)

        self.draw_focused_block()
        self.set_2d()
        self.draw_reticle()

        glDisable(GL_COLOR_LOGIC_OP)
        glColor3d(1, 1, 1)
        self.model.hud_batch.draw()
        
        if self.debug_info_visible:
            self.draw_debug_info()
    
    def draw_debug_info(self):
        """
        draw stuff like Position, Rotation, FPS, ...
        """
        x, y, z = self.position
        fps = pyglet.clock.get_fps()
        queue = len(self.model.queue)
        face_buffer = len(self.model.blockface_update_buffer)
        terrain_queue = len(self.model.init_chunk_queue.chunks)
        
        self.label.text = 'FPS: %03d \t Position: (%.2f, %.2f, %.2f) \t Buffer: %04d, %04d, %04d' % (fps, x, y, z, queue, face_buffer, terrain_queue)
        self.label.draw()
        

    def draw_focused_block(self):
        """
        Draw black edges around the block that is currently under the
        crosshairs.
        """
        vector = self.get_sight_vector()
        if CHUNKSIZE == None:
            return
        block = Ray(self.position, vector).hit_test(lambda pos:self.model.get_block(pos)!="AIR", focus_distance)[1]
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

def setup_fog():
    """
    Configure the OpenGL fog properties.
    """
    # Enable fog. Fog "blends a fog color with each rasterized pixel fragment's
    # post-texturing color."
    glEnable(GL_FOG)
    # Set the fog color.
    glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1))
    # Say we have no preference between rendering speed and quality.
    glHint(GL_FOG_HINT, GL_DONT_CARE)
    # Specify the equation used to compute the blending factor.
    glFogi(GL_FOG_MODE, GL_LINEAR)
    # How close and far away fog starts and ends. The closer the start and end,
    # the denser the fog in the fog range.
    glFogf(GL_FOG_START, 20.0)
    glFogf(GL_FOG_END, 60.0)

def setup_shaders():
    global fancy_block_shader, plain_block_shader
    glEnable(GL_NORMALIZE)
    fancy_block_shader = Shader([vertex_shader_code], [fancy_fragment_shader_code])
    plain_block_shader = Shader([vertex_shader_code], [plain_fragment_shader_code])

def setup():
    """ Basic OpenGL configuration.

    """
    # Set the color of "clear", i.e. the sky, in rgba.
    glClearColor(0.5, 0.69, 1.0, 1)
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
        # receive texturedata from game
        while True:
            c = client.receive()
            if c:
                if c.startswith("setup"):
                    setup_src = json.loads(c.split(" ",1)[-1])
                    port = setup_src.setdefault("port",80)
                    host = setup_src.setdefault("host",client.socket.getpeername()[0])
                    load_setup(host,port)
                    break
                else:
                    print(c)
                    raise ValueError("got unexpected message while waiting for setup")
        if options.name:
            entity_id = options.name
            password = options.password
            if not options.password:
                print("Consider setting a password when using a name.")
        else:
            entity_id = random.getrandbits(32)
            password = random.getrandbits(32)
            if options.password:
                print("Ignoring user set password because no name was given.")
        client.send("control %s %s"%(entity_id, password))
        #setup_shaders()
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

def get_servers():
    if options.host and options.port:
        return [((options.host, options.port),"Direct Connection")]
    servers = socket_connection.search_servers(key="voxelgame"+options.parole)
    print(servers)
    if options.host:
        servers[:] = [server for server in servers if server[0][0] == options.host]
    if options.port:
        servers[:] = [server for server in servers if server[0][1] == options.port]
    return servers
    
def run(addr):
    print(addr)
    try:
        with socket_connection.client(addr) as socket_client:
            show_on_window(socket_client)
    except socket_connection.Disconnect:
        print("Client closed due to disconnect.")

def main():
    servers = get_servers()
    print(servers)
    if len(servers) == 0:
        print("No Server found.")
        time.sleep(1)
        return
    elif len(servers) == 1:
        addr = servers[0][0]
    else:
        print("SELECT SERVER")
        addr = servers[select([i[1] for i in servers])[0]][0]
    run(addr)

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-H",
              "--host", dest="host",
              help="only consider servers on this HOST", metavar="HOST",
              action="store")
parser.add_option("-P",
              "--port", dest="port",
              help="only consider servers on this PORT", metavar="PORT", type="int",
              action="store")
parser.add_option(
              "--parole", dest="parole",
              help="find servers with this parole", metavar="PAROLE", default="",
              action="store")
parser.add_option("-N",
              "--name", dest="name",
              help="use this name for playing on the server", metavar="NAME",
              action="store")
parser.add_option(
              "--password", dest="password",
              help="set a password to prevent others from connecting with your name", metavar="PASSWORD",
              action="store")
options, args = parser.parse_args()
if __name__ == '__main__':
    main()
