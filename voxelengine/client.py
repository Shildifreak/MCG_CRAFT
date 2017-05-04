# -*- coding: cp1252 -*-
import math
import time
import sys, os
import inspect
import warnings
from collections import deque
import itertools
import ast
from __init__ import Vector, Chunk

# Adding directory with modules to python path
PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(os.path.join(PATH,"modules"))

import pyglet
from pyglet import image
#pyglet.options["debug_gl"] = False
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse

import socket_connection
from shared import *


TICKS_PER_SEC = 60

def cube_vertices(x, y, z, n):
    """ Return the vertices of the cube at position x, y, z with size 2*n.

    """
    return [
        x-n,y+n,z-n, x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n,  # top
        x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n,  # bottom
        x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n,  # left
        x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n,  # right
        x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n,  # front
        x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n,  # back
    ]

def face_vertices(x, y, z, f, n):
    return (
        [x-n,y+n,z-n, x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n],  # top
        [x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n],  # bottom
        [x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n],  # left
        [x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n],  # right
        [x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n],  # front
        [x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n],  # back
    )[f]

def face_vertices_noncube(x, y, z, f, size):
    dx,dy,dz = size
    return (
        [x-dx,y+dy,z-dz, x-dx,y+dy,z+dz, x+dx,y+dy,z+dz, x+dx,y+dy,z-dz],  # top
        [x-dx,y-dy,z-dz, x+dx,y-dy,z-dz, x+dx,y-dy,z+dz, x-dx,y-dy,z+dz],  # bottom
        [x-dx,y-dy,z-dz, x-dx,y-dy,z+dz, x-dx,y+dy,z+dz, x-dx,y+dy,z-dz],  # left
        [x+dx,y-dy,z+dz, x+dx,y-dy,z-dz, x+dx,y+dy,z-dz, x+dx,y+dy,z+dz],  # right
        [x-dx,y-dy,z+dz, x+dx,y-dy,z+dz, x+dx,y+dy,z+dz, x-dx,y+dy,z+dz],  # front
        [x+dx,y-dy,z-dz, x-dx,y-dy,z-dz, x-dx,y+dy,z-dz, x+dx,y+dy,z-dz],  # back
    )[f]

def tex_coord(x, y):
    """ Return the bounding vertices of the texture square.

    """
    m = 1.0 / TEXTURE_SIDE_LENGTH
    dx = x * m
    dy = y * m
    
    p = TEXTURE_EDGE_CUTTING*m
    dx += p
    dy += p
    m  -= p * 2
    
    return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m


def tex_coords(textures):
    """ Return a list of the texture squares for the top, bottom and side.

    """
    result = []
    for i in range(6):
        if i >= len(textures):
            i = -1
        result.append(tex_coord(*textures[i]))
    return result

def load_setup(path):
    global CHUNKSIZE, TEXTURES, TRANSPARENCY, focus_distance, TEXTURE_SIDE_LENGTH, TEXTURE_PATH, TEXTURE_EDGE_CUTTING, ENTITY_MODELS, BLOCK_ID_BY_NAME
    setupfile = open(path,"r")
    setup = ast.literal_eval(setupfile.read())
    CHUNKSIZE = setup["CHUNKSIZE"]
    focus_distance = setup["DEFAULT_FOCUS_DISTANCE"]
    TEXTURE_SIDE_LENGTH = setup["TEXTURE_SIDE_LENGTH"]
    TEXTURE_EDGE_CUTTING = setup.get("TEXTURE_EDGE_CUTTING",0)
    ENTITY_MODELS = setup.get("ENTITY_MODELS",{})
    if not os.path.isabs(setup["TEXTURE_PATH"]): #M# do something to support urls
        setup["TEXTURE_PATH"] = os.path.join(os.path.dirname(path),setup["TEXTURE_PATH"])
    TEXTURE_PATH = setup["TEXTURE_PATH"]
    TEXTURES = [None] #this first value is for air
    TRANSPARENCY = [True]
    BLOCK_ID_BY_NAME = {"AIR":0}
    for i, (name, transparency, solidity, textures) in enumerate(setup["TEXTURE_INFO"]):
        BLOCK_ID_BY_NAME[name] = i+1
        TEXTURES.append(tex_coords(textures))
        TRANSPARENCY.append(transparency)


FACES = [Vector([ 0, 1, 0]), #top
         Vector([ 0,-1, 0]), #bottom
         Vector([-1, 0, 0]), #left
         Vector([ 1, 0, 0]), #right
         Vector([ 0, 0, 1]), #front
         Vector([ 0, 0,-1])] #back

class SimpleChunk(object):
    def __init__(self):
        self.blocks = {}

    def get_block(self,position):
        return self.blocks.get(position,0 if self.blocks else None)

    def set_block(self,position,value):
        if value == 0:
            del self.blocks[position]
        else:
            self.blocks[position] = value

def iterchunk():
    return itertools.product(*(xrange(1<<CHUNKSIZE),)*DIMENSION)

def iterframe():
    for de in (-1,1<<CHUNKSIZE):
        for d1 in xrange(1<<CHUNKSIZE):
            for d2 in xrange(1<<CHUNKSIZE):
                yield (de,d1,d2)
                yield (d1,de,d2)
                yield (d1,d2,de)

class Chunkdict(dict):
    def __missing__(self, chunkposition):
        chunk = SimpleChunk()
        self[chunkposition] = chunk
        return chunk

class Model(object):

    def __init__(self):

        # A Batch is a collection of vertex lists for batched rendering.
        self.batch = pyglet.graphics.Batch()

        # A TextureGroup manages an OpenGL texture.
        self.group = TextureGroup(image.load(TEXTURE_PATH).get_texture()) #possible to use image.load(file=filedescriptor) if necessary

        self.shown = {} #{(position,face):vertex_list(batch_element)}
        self.chunks = Chunkdict()
        self.entities = {} #{entity_id: (vertex_list,...,...)}

        self.queue = deque()

    def add_block(self,position, id_or_name):
        """for immediate execution use private method"""
        self.queue.append((self._add_block,(position,id_or_name)))

    def remove_block(self, position):
        """for immediate execution use private method"""
        self.queue.append((self._remove_block,(position,)))

    def clear(self):
        """for immediate execution use private method"""
        self.queue.append((self._clear,()))

    def del_area(self, position):
        """for immediate execution use private method"""
        self.queue.append((self._del_area,(position,)))

    def set_area(self, position, compressed_blocks):
        """for immediate execution use private method"""
        self.queue.append((self._set_area,(position,compressed_blocks)))

    def process_queue(self):
        start = time.clock()
        while self.queue and time.clock() - start < 1.0 / TICKS_PER_SEC:
            func,args = self.queue.popleft()
            func(*args)

    def update_visibility(self, position):
        if self.get_block(position):
            for f in xrange(len(FACES)):
                self.update_face(position,f)

    def update_face(self,position,face):
        fv = FACES[face]
        b = self.get_block(position+fv)
        if b != None:
            if b == 0: #M# test for transparency here!
                self.show_face(position,face)
                return
        self.hide_face(position,face)
    
    def update_visibility_around(self,position):
        for f,fv in enumerate(FACES):
            self.update_face(position+fv,(f+1-(2*(f%2))))
    
    def show_face(self,position,face):
        if (position,face) in self.shown:
            #M# entscheiden ob entweder sicher:
            #self.hide_face(position,face)
            #M# oder schnell:
            return
        x, y, z = position
        block_id = self.get_block(position)
        if not block_id:
            return
        texture_data = list(TEXTURES[block_id][face])
        vertex_data = face_vertices(x, y, z, face, 0.5)
        # create vertex list
        # FIXME Maybe `add_indexed()` should be used instead
        self.shown[(position,face)] = self.batch.add(4, GL_QUADS, self.group,
            ('v3f/static', vertex_data),
            ('t2f/static', texture_data))

    def hide(self,position):
        for face in xrange(len(FACES)):
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
                    texture = entity_id%len(TEXTURES)
                if isinstance(texture,basestring):
                    texture = BLOCK_ID_BY_NAME[texture]
                for face in range(len(FACES)):
                    texture_data = list(TEXTURES[texture][face])
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
                    vertex_lists.append(self.batch.add(4, GL_QUADS, self.group,
                        ('v3f/static', vertex_data),
                        ('t2f/static', texture_data)))
        self.entities[entity_id] = vertex_lists

    def del_entity(self,entity_id):
        vertex_lists = self.entities.pop(entity_id,[])
        for vertex_list in vertex_lists:
            vertex_list.delete()

    def _add_block(self, position, block_id):
        if self.get_block(position):
            self.hide(position)
        self._set_block(position,block_id)
        self.update_visibility(position)
        self.update_visibility_around(position)

    def _remove_block(self, position):
        self._set_block(position,0)
        self.hide(position)
        self.update_visibility_around(position)

    def _clear(self):
        for position,face in self.shown.keys():
            self.hide_face(position,face)
        self.shown = {}
        self.chunks = Chunkdict()

    def _del_area(self, position):
        self.chunks[position] = SimpleChunk()
        for relpos in iterchunk():
            self.hide((position<<CHUNKSIZE)+relpos)
        for relpos in iterframe():
            #M# hier müsste eigentlich immer nur die entsprechende Seite upgedated werden
            self.update_visibility((position<<CHUNKSIZE)+relpos)
        del self.chunks[position] #M# maybe someday empty SimpleChunks will be deleted automatically

    def _set_area(self, position, compressed_blocks):
        if isinstance(self.chunks[position],Chunk):
            raise Exception("Can't load chunk if there is already one.")
        c = Chunk(CHUNKSIZE)
        self.chunks[position] = c
        c.compressed_data = compressed_blocks

        for i,relpos in enumerate(iterchunk()):
            if c[i] != 0: #wird zwar in update_visibility auch noch mal geprüft, ist aber so schneller
                self.update_visibility((position<<CHUNKSIZE)+relpos)
        for relpos in iterframe():
            #M# hier gilt das selbe wie in _del_chunk
            self.update_visibility((position<<CHUNKSIZE)+relpos)

    def get_block(self,position):
        return self.chunks[position>>CHUNKSIZE].get_block(position)

    def _set_block(self,position,block_id):
        """this does not update the screen!"""
        return self.chunks[position>>CHUNKSIZE].set_block(position,block_id)

class Window(pyglet.window.Window):

    def __init__(self, client = None, *args, **kwargs):
        # The crosshairs at the center of the screen.
        self.reticle = None
        # (has to be called before standart init which sometimes calls on_resize)

        pyglet.window.Window.__init__(self,*args, **kwargs)
        #super(Window, self).__init__(*args, **kwargs)

        # Whether or not the window exclusively captures the mouse.
        self.exclusive = False

        # Current (x, y, z) position in the world, specified with floats. Note
        # that, perhaps unlike in math class, the y-axis is the vertical axis.
        self.position = (0, 0, 0)

        # First element is rotation of the player in the x-z plane (ground
        # plane) measured from the z-axis down. The second is the rotation
        # angle from the ground plane up. Rotation is in degrees.
        #
        # The vertical plane rotation ranges from -90 (looking straight down) to
        # 90 (looking straight up). The horizontal rotation range is unbounded.
        self.rotation = (0, 0)

        # Instance of the model that handles the world.
        self.model = Model()

        # This call schedules the `update()` method to be called
        # TICKS_PER_SEC. This is the main game event loop.
        pyglet.clock.schedule_interval(self.update, 1.0 / TICKS_PER_SEC)
        self.updating = False #make sure there is only 1 update function per time

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
        """ If `exclusive` is True, the game will capture the mouse, if False
        the game will ignore the mouse.

        """
        #pyglet.window.Window.set_exclusive_mouse(self,exclusive)
        super(Window, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive

    def get_sight_vector(self):
        """ Returns the current line of sight vector indicating the direction
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
        if self.updating:
            return
        self.updating = True
        while True:
            c = self.client.receive(0.001)
            if not c:
                break
            if c.startswith("setarea"):
                c = c.split(" ",4)
                position = Vector(map(int,c[1:4]))
                compressed_blocks = c[4]
                self.model.set_area(position,compressed_blocks)
                continue
            c = c.split(" ")
            #M# maybe define this function somewhere else
            def test(name,argc):
                if name == c[0]:
                    if len(c) == argc:
                        return True
                    print "Falsche Anzahl von Argumenten bei %s" %name
                return False
            if test("clear",1):
                self.model.clear()
            elif test("del",4):
                position = Vector(map(int,c[1:4]))
                self.model.remove_block(position)
            elif test("delarea",4):
                position = Vector(map(int,c[1:4]))
                self.model.del_area(position)
            elif test("set",5):
                position = Vector(map(int,c[1:4]))
                self.model.add_block(position,int(c[4]))
            elif test("goto",4):
                position = Vector(map(float,c[1:4]))
                self.position = position
            elif test("focusdist",2):
                focus_distance = float(c[1])
            elif test("setentity",8):
                position = Vector(map(float,c[3:6]))
                rotation = map(float,c[6:8])
                self.model.set_entity(int(c[1]),c[2],position,rotation)
            elif test("delentity",2):
                self.model.del_entity(int(c[1]))
            else:
                print "unknown command", c
        self.client.send("tick")
        self.model.process_queue()
        self.updating = False

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.client.send("scrolling: "+str(scroll_y))
        
    def on_mouse_press(self, x, y, button, modifiers):
        """ Called when a mouse button is pressed. See pyglet docs for button
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
        if self.exclusive:
            if (button == mouse.RIGHT) or \
                    ((button == mouse.LEFT) and (modifiers & key.MOD_CTRL)):
                # ON OSX, control + left click = right click.
                self.client.send("right click")
            elif button == pyglet.window.mouse.LEFT:
                self.client.send("left click")
        else:
            self.set_exclusive_mouse(True)

    def on_mouse_motion(self, x, y, dx, dy):
        """ Called when the player moves the mouse.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
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
        """ Called when the player presses a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """
        # Mapping of keys to events
        keymap = [(key._1    ,"inv1" ),
                  (key._2    ,"inv2" ),
                  (key._3    ,"inv3" ),
                  (key._4    ,"inv4" ),
                  (key._5    ,"inv5" ),
                  (key._6    ,"inv6" ),
                  (key._7    ,"inv7" ),
                  (key._8    ,"inv8" ),
                  (key._9    ,"inv9" ),
                  (key._0    ,"inv0" ),
                  (key.W     ,"for"  ),
                  (key.S     ,"back" ),
                  (key.A     ,"left" ),
                  (key.D     ,"right"),
                  (key.SPACE ,"jump" ),
                  (key.TAB   ,"fly"  ),
                  (key.E     ,"inv"  ),
                  (key.LSHIFT,"shift"),
                  ]
        used_keys = set([i[0] for i in keymap])
        eventstates = int(bool(modifiers & key.MOD_CTRL))
        if symbol in used_keys:
            for k,e in keymap:
                if self.keystates[k]:
                    eventstates |= 1<<(ACTIONS.index(e)+1)
            self.client.send("keys "+str(eventstates))

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.set_exclusive_mouse(False)
        else:
            self.send_key_change(symbol, modifiers, True)
                
    def on_key_release(self, symbol, modifiers):
        self.send_key_change(symbol, modifiers, False)

    def on_resize(self, width, height):
        """ Called when the window is resized to a new `width` and `height`.

        """
        # reticle
        if self.reticle:
            self.reticle.delete()
        x, y = self.width // 2, self.height // 2
        n = 10
        self.reticle = pyglet.graphics.vertex_list(4,
            ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
        )

    def set_2d(self):
        """ Configure OpenGL to draw in 2d.

        """
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_3d(self):
        """ Configure OpenGL to draw in 3d.

        """
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65.0, width / float(height), 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        yaw, pitch = self.rotation
        c = math.cos(math.radians(yaw))
        s = math.sin(math.radians(yaw))
        glRotatef(yaw, 0, 1, 0)
        glRotatef(-pitch, c, 0, s)
        AH = 0.5
        dx = 0#AH* math.sin(math.radians(pitch))*-s
        dz = 0#AH* math.sin(math.radians(pitch))*c
        dy = 0#AH*(math.cos(math.radians(pitch))-1)
        x, y, z = self.position
        glTranslatef(-x-dx, -y-dy, -z-dz)

    def on_draw(self):
        """ Called by pyglet to draw the canvas.

        """
        self.clear()
        self.set_3d()
        glColor3d(1, 1, 1)
        self.model.batch.draw()
        
        x = 0.25 #1/(Potenzen von 2) sind sinnvoll, je größer der Wert, desto stärker der Kontrast
        glColor3d(x, x, x)
        #glEnable(GL_BLEND)
        #glBlendFunc(GL_ONE_MINUS_DST_COLOR, GL_ZERO)
        glEnable(GL_COLOR_LOGIC_OP)
        glLogicOp(GL_XOR)

        self.draw_focused_block()
        self.set_2d()
        self.draw_reticle()

        glDisable(GL_COLOR_LOGIC_OP)
        #glDisable(GL_BLEND)
        #M# self.model.hud_batch.draw()

    def draw_focused_block(self):
        """ Draw black edges around the block that is currently under the
        crosshairs.

        """
        vector = self.get_sight_vector()
        block = hit_test(self.model.get_block, self.position, vector, focus_distance)[0]
        if block:
            x, y, z = block
            vertex_data = cube_vertices(x, y, z, 0.51)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            pyglet.graphics.draw(24, GL_QUADS, ('v3f/static', vertex_data))
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def draw_reticle(self):
        """ Draw the crosshairs in the center of the screen.

        """
        self.reticle.draw(GL_LINES)

def setup_fog():
    """ Configure the OpenGL fog properties.

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

    setup_fog()

def show_on_window(client):
    window = None
    try:
        # receive texturedata from game
        while True:
            c = client.receive()
            if c and c.startswith("setup"):
                path = c.split(" ",1)[-1]
                load_setup(path)
                break
        window = Window(width=800, height=600, caption='MCG-Craft 1.0.4',
                        resizable=True,client=client)
        # Hide the mouse cursor and prevent the mouse from leaving the window.
        window.set_exclusive_mouse(True)
        setup()
        pyglet.app.run()
    except Exception as e:
        raise
        if e.message != "Disconnect" and e.message != "Server went down.":
            raise
        else:
            print e.message
    finally:
        if window:
            window.on_close()

def main(socket_client = None):
    if socket_client == None:
        servers = socket_connection.search_servers(key="voxelgame")
        if servers:
            print "SELECT SERVER"
            addr = servers[select([i[1] for i in servers])[0]][0]
            with socket_connection.client(addr) as socket_client:
                show_on_window(socket_client)
        else:
            print("No Server found.")
            time.sleep(1)

    else:
        if "-debug" in sys.argv:
            print "doing something clienty"
        show_on_window(socket_client)

def autoclient():
    while True:
        main()
        time.sleep(10)

if __name__ == '__main__':
    #autoclient()
    main()
