# -*- coding: cp1252 -*-
import math
import time
import sys, os
import inspect
import warnings
from collections import deque


# Adding directory with pyglet to python path
PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(os.path.dirname(PATH.rstrip(os.path.sep)))

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

def tex_coord(x, y, n=16):
    """ Return the bounding vertices of the texture square.

    """
    m = 1.0 / n
    dx = x * m
    dy = y * m
    return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m


def tex_coords(top, bottom, side):
    """ Return a list of the texture squares for the top, bottom and side.

    """
    top = tex_coord(*top)
    bottom = tex_coord(*bottom)
    side = tex_coord(*side)
    result = []
    result.extend(top)
    result.extend(bottom)
    result.extend(side * 4)
    return result

TEXTURE_PATH = os.path.join(PATH,'texture.png')

import textures
TEXTURES = [None]
BLOCK_ID_BY_NAME = {"AIR":0}
for name, top, bottom, side in textures.textures:
    BLOCK_ID_BY_NAME[name] = len(TEXTURES)
    TEXTURES.append(tex_coords(top, bottom, side))

FACES = [
    ( 0, 1, 0),
    ( 0,-1, 0),
    (-1, 0, 0),
    ( 1, 0, 0),
    ( 0, 0, 1),
    ( 0, 0,-1),
]

class Model(object):

    def __init__(self):

        # A Batch is a collection of vertex lists for batched rendering.
        self.batch = pyglet.graphics.Batch()

        # A TextureGroup manages an OpenGL texture.
        self.group = TextureGroup(image.load(TEXTURE_PATH).get_texture())

        self.blocks = {}

        self.queue = deque()

    def add_block(self,position, id_or_name):
        self.queue.append((self._add_block,(position,id_or_name)))

    def remove_block(self, position):
        self.queue.append((self._remove_block,(position,)))

    def clear(self):
        self.queue.append((self._clear,()))

    def del_area(self, position, chunksize):
        self.queue.append((self._del_area,(position,chunksize)))

    def set_area(self, position, chunksize, blocknumber, block_id):
        self.queue.append((self._set_area,(position,chunksize,blocknumber,block_id)))

    def process_queue(self):
        start = time.clock()
        while self.queue and time.clock() - start < 1.0 / TICKS_PER_SEC:
            func,args = self.queue.popleft()
            func(*args)

    def _add_block(self, position, id_or_name):
        if position in self.blocks:
            self.remove_block(position)
        x, y, z = position
        try:
            block_id = int(id_or_name)
        except ValueError:
            block_id = BLOCK_ID_BY_NAME[id_or_name]
        if block_id == 0:
            return
        texture_data = list(TEXTURES[block_id])
        vertex_data = cube_vertices(x, y, z, 0.5)
        # create vertex list
        # FIXME Maybe `add_indexed()` should be used instead
        self.blocks[position] = self.batch.add(24, GL_QUADS, self.group,
            ('v3f/static', vertex_data),
            ('t2f/static', texture_data))

    def _remove_block(self, position):
        if not position in self.blocks:
            return False
        self.blocks.pop(position).delete()

    def _clear(self):
        for position in self.blocks.keys():
            self.remove_block(position)

    def _del_area(self, position, chunksize):
        for dx in range(chunksize):
            for dy in range(chunksize):
                for dz in range(chunksize):
                    self.remove_block(position+(dx,dy,dz))

    def _set_area(self, position, chunksize, blocknumber, block_id):
        chunkpos = (position>>chunksize)<<chunksize
        x,y,z = position%(1<<chunksize)
        for i in range(blocknumber):
            self.add_block(chunkpos+(x,y,z),block_id)
            z += 1
            x += z//(1<<chunksize); z%=(1<<chunksize)
            y += x//(1<<chunksize); x%=(1<<chunksize)

    def block_at(self,position):
        return position in self.blocks

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

        # some blocks to see if client works as intended
        self.model.add_block((1,2,3),"GRASS")

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
        if self.updating:
            return
        self.updating = True
        while True:
            c = self.client.receive(0.001)
            if not c:
                break
            #print c
            c = c.split(" ")
            def test(name,argc):
                if name == c[0]:
                    if len(c) == argc:
                        return True
                    print "Falsche Anzahl von Argumenten bei %s" %name
                return False
            if test("clear",0):
                self.model.clear()
            elif test("del",4):
                position = Vector(map(int,c[1:4]))
                self.model.remove_block(position)
            elif test("delarea",5):
                chunksize = int(c[1])
                position = Vector(map(int,c[2:5]))
                self.model.del_area(position,chunksize)
            elif test("set",5):
                position = Vector(map(int,c[1:4]))
                self.model.add_block(position,c[4])
            elif test("setarea",7):
                position = Vector(map(int,c[1:4]))
                chunksize = int(c[4])
                blocknumber = int(c[5])
                block_id = c[6]
                self.model.set_area(position,chunksize,blocknumber,block_id)
            elif test("goto",4):
                position = Vector(map(float,c[1:4]))
                self.position = position
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
        x, y = self.width / 2, self.height / 2
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
        x, y = self.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.position
        glTranslatef(-x, -y, -z)

    def on_draw(self):
        """ Called by pyglet to draw the canvas.

        """
        self.clear()
        self.set_3d()
        glColor3d(1, 1, 1)
        self.model.batch.draw()
        self.draw_focused_block()
        self.set_2d()
        self.draw_reticle()

    def draw_focused_block(self):
        """ Draw black edges around the block that is currently under the
        crosshairs.

        """
        vector = self.get_sight_vector()
        block = hit_test(self.model.block_at, self.position, vector)[0]
        if block:
            x, y, z = block
            vertex_data = cube_vertices(x, y, z, 0.51)
            glColor3d(0, 0, 0)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            pyglet.graphics.draw(24, GL_QUADS, ('v3f/static', vertex_data))
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def draw_reticle(self):
        """ Draw the crosshairs in the center of the screen.

        """
        glColor3d(0, 0, 0)
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
        print "doing something clienty"
        show_on_window(socket_client)

def autoclient():
    while True:
        main()
        time.sleep(10)

if __name__ == '__main__':
    #autoclient()
    main()
