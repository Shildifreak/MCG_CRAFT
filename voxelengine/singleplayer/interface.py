import thread
import time
import warnings

# Fixing some unexpected behaviour (aka bug) when importing pyglet without it actually being in the python path
import sys, os, inspect
PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
warnings.warn("adding %s to sys.path to work around bug in pyglet" %PATH,Warning)
sys.path.append(PATH)

class Blockworld(object):
   
    def __init__(self, threaded=True,updatemethod=lambda:None):
        """create new Blockworld instance with window"""
        self.initialised = False
        self.mousestates = {}
        self.updatemethod = updatemethod
        if threaded:
            thread.start_new_thread(self._init,())
            while not self.is_init():
                time.sleep(0.1)
        else:
            self._init()
        
    def _init(self):
        """all pyglet stuff must be done in the same thread"""
        # yes I know, this one looks really dirty
        # but the import has to be in the same thread like all
        # the other stuff and the monkeypatching and subclassing
        # can only be done after the import.
        # Everything would be so simple if I just changed the main.py
        import main
        reload(main)

        main.TEXTURE_PATH = os.path.join(PATH,"texture.png")

        main.Model._initialize = staticmethod(lambda:None)
        main.Model.process_queue = main.Model.process_entire_queue

        class Window(main.Window):
            blockworld = self
            def _update(self,dt):
                self.blockworld.updatemethod()

            def on_key_press(self,symbol,modifiers):
                if symbol == main.key.ESCAPE:
                    self.set_exclusive_mouse(not self.exclusive)

            def on_key_release(self,symbol,modifiers):
                pass

            def on_mouse_press(self, x, y, button, modifiers, mousestates=self.mousestates):
                self.blockworld.mousestates[button] = True
                if not self.exclusive:
                    self.set_exclusive_mouse(True)

            def on_mouse_release(self, x, y, button, modifiers, mousestates=self.mousestates):
                self.blockworld.mousestates[button] = False

            def on_deactivate(self):
                self.blockworld.keystates.clear()

            def on_close(self):
                # tell blockworld that the Window should not be used anymore
                self.blockworld.initialised = False
                # try to close it, althought this seems to raise a lot of errors
                self.close()
                main.pyglet.app.exit()

        # create window
        window = Window(width=800, height=600, caption="interface", resizable = True)
        # make objects accessible from other thread
        self.window = window
        self.model = window.model
        self.TEXTURES = (main.GRASS, main.SAND, main.BRICK, main.STONE)
        # Hide the mouse cursor and prevent the mouse from leaving the window.
        window.set_exclusive_mouse(True)
        # key state handler
        self.keystates = main.key.KeyStateHandler()
        self.window.push_handlers(self.keystates)
        self.keymap = {"up": (lambda:self.keystates[main.key.UP]),
                       "down": (lambda:self.keystates[main.key.DOWN]),
                       "left": (lambda:self.keystates[main.key.LEFT]),
                       "right": (lambda:self.keystates[main.key.RIGHT]),
                       "space": (lambda:self.keystates[main.key.SPACE]),
                       "leftclick": (lambda:self.mousestates.get(main.mouse.LEFT,False)),
                       "rightclick": (lambda:self.mousestates.get(main.mouse.RIGHT,False)),
                       }
        # run setup
        main.setup()
        # signalise init is done
        self.initialised = True
        # launch app
        main.pyglet.app.run()

    def is_init(self):
        """returns True if Window is open and Blockworld ready to use"""
        return self.initialised

    def get_block(self,(x,y,z)):
        """return ID of block at x,y,z"""
        texture = self.model.world.get((x,y,z),None)
        if texture == None:
            return None
        return self.TEXTURES.index(texture)

    def set_block(self,(x,y,z),BlockID=None):
        """set ID of block at x,y,z"""
        if BlockID != None:
            texture = self.TEXTURES[BlockID]
            self.model._enqueue(self.model.add_block, (x,y,z), texture)
        else:
            self.model._enqueue(self.model.remove_block, (x,y,z))

    def get_pos(self):
        """return position of camera/player"""
        return self.window.position

    def set_pos(self,(x,y,z)):
        """set position of camera/player"""
        self.window.position = (x,y,z)

    def get_focused_pos(self,max_distance=8):
        """return position of block the player is pointing at
        returns None if there is no block within max_distance"""
        return self.model.hit_test(self.window.position,
                                   self.window.get_sight_vector(),
                                   max_distance)[0]

    def get_sight_vector(self):
        """ Returns the current line of sight vector indicating the direction
        the player is looking.
        """
        return self.window.get_sight_vector()

    def get_state(self,key):
        statemap,rawkey = self.keymap[key]
        return statemap[rawkey]

    def get_pressed(self):
        return [k for k,v in self.keymap.iteritems() if v()]+\
            [k for k,v in self.keystates.iteritems() if v]

if __name__ == "__main__":
    b = Blockworld()

    for x in xrange(-20, 21):
        for z in xrange(-20, 21):
            # create a layer stone and grass everywhere.
            b.set_block((x,1,z),0)
            b.set_block((x,0,z),3)
    b.set_pos((0,3,0))
    while b.is_init():
        time.sleep(0.1)
        print b.get_pressed()
