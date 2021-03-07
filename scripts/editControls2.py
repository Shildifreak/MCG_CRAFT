#* encoding: utf-8 *#

import sys, os, inspect
PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(os.path.join(PATH,"..","lib","voxelengine","modules"))
import collections
import appdirs
import pyglet
from pyglet.window import key, mouse

configdir = appdirs.user_config_dir("MCGCraft","ProgrammierAG")
configfn = os.path.join(configdir,"desktopclientsettings.py")
print(configfn)
if os.path.exists(configfn):
    with open(configfn) as configfile:
        try:
            config = eval(configfile.read(),globals())
        except:
            config = {}
else:
    config = {}

if (not "controls" in config) or (not isinstance(config["controls"], list)):
    config["controls"] = []

#update from old format
if len(config["controls"]) > 0 and not isinstance(config["controls"][0], dict):
    old_controls = config["controls"]
    new_controls = [{action: event for event, action in old_controls}]
    config["controls"] = new_controls

actions = [
    ("left_hand", u"linke Hand"),
    ("right_hand", u"rechte Hand"),
    ("mine", u"Block abbauen"),
    ("activate", u"Block aktivieren"),
    ("for",  u"vorwärts laufen"),
    ("back", u"rückwärts laufen"),
    ("left", "nach links laufen"),
    ("right", "nach rechts laufen"),
    ("jump", u"hüpfen"),
    ("fly", "Flugmodus aktivieren"),
    ("inv", u"Inventar öffnen/schließen"),
    ("shift", u"ducken + mod. Mausfunktionen"),
    ("sprint", u"sprinten"),
    ("emote", u"Grimasse schneiden"),
    ("chat", u"Chat öffnen"),
    ("inv1", u"Inventarplatz 1"),
    ("inv2", u"Inventarplatz 2"),
    ("inv3", u"Inventarplatz 3"),
    ("inv4", u"Inventarplatz 4"),
    ("inv5", u"Inventarplatz 5"),
    ("inv6", u"Inventarplatz 6"),
    ("inv7", u"Inventarplatz 7"),
    ("inv8", u"Inventarplatz 8"),
    ("inv9", u"Inventarplatz 9"),
    ("inv0", u"Inventarplatz 10"),
    ("inv+", u"nächster Inventarplatz"),
    ("inv-", u"vorheriger Inventarplatz"),

    # client only actions
    ("+yaw", u"Kamera rechts"),
    ("-yaw", u"Kamera links"),
    ("+pitch", u"Kamera hoch"),
    ("-pitch", u"Kamera runter"),
    ("hud_up", u"HUD Auswahl hoch"),
    ("hud_down", u"HUD Auswahl runter"),
    ("hud_left", u"HUD Auswahl links"),
    ("hud_right", u"HUD Auswahl rechts"),
    ]

ACTION_LABEL_WIDTH  = 300
KEY_LABEL_WIDTH     = 100
ROW_HEIGHT = 20
FONT_SIZE = 16

window = pyglet.window.Window(1000,ROW_HEIGHT*(len(actions)+2),"Edit Controls 2")

recording = None # None or (action_index, control_layer_index)
changed_since_save = False

@window.event
def on_draw():
    window.clear()
    if recording == None:
        batch.draw()
    else:
        recording_label.text = "Recording Event for " + actions[recording[0]][1]
        recording_label.draw()

def assign_action(event_type, event_id):
    global recording, changed_since_save
    if recording == None:
        return
    event = (event_type, event_id)
    print(event, recording)
    action_index, control_layer_index = recording
    action_name, _ = actions[action_index]
    while len(config["controls"]) <= control_layer_index:
        config["controls"].append({})
    config["controls"][control_layer_index][action_name] = event
    changed_since_save = True
    update_table()
    recording = None

@window.event
def on_key_press(key, modifiers):
    assign_action("key", key)

@window.event
def on_mouse_press(x, y, button, modifiers):
    global recording, changed_since_save
    if recording == None:
        action_index = int((window.height-y) // ROW_HEIGHT) - 2
        control_layer_index = int((x - ACTION_LABEL_WIDTH) // KEY_LABEL_WIDTH)
        if (action_index < 0 and control_layer_index < 0):
            if changed_since_save:
                # save
                with open(configfn,"w") as configfile:
                    configfile.write(repr(config))
            changed_since_save = False
            update_table()
        if not (0 <= action_index < len(actions)):
            return
        if control_layer_index < 0:
            return
        if button == mouse.LEFT:
            for joystick in joysticks:
                reset_resting_positions(joystick)
            recording = (action_index, control_layer_index)
        elif button == mouse.RIGHT:
            if control_layer_index < len(config["controls"]):
                action_name, _ = actions[action_index]
                config["controls"][control_layer_index].pop(action_name, None)
                changed_since_save = True
                update_table()
    else:
        assign_action("mouse", button)
    
@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    if abs(scroll_x) > abs(scroll_y):
        if scroll_x > 0:
            assign_action("scroll","right")
        else:
            assign_action("scroll","left")
    else:
        if scroll_y > 0:
            assign_action("scroll","up")
        else:
            assign_action("scroll","down")

class JoystickHandler(object):
    THRESHOLD = 0.9
    def __init__(self):
        self.axis_states = collections.defaultdict(bool)
    
    def on_joybutton_press(self, joystick, button):
        assign_action("joystick", "button_%i"%button)

    def on_joyaxis_motion(self, joystick, axis, value):
        global recording
        resting_position = joystick.resting_positions.get(axis, None)
        if resting_position == None:
            joystick.resting_positions[axis] = 0
            assign_action("error","please retry")
            return
        if resting_position <= -self.THRESHOLD:
            self._on_joyaxis_motion(joystick, "trigger_%s"%axis, (value+1)/2)
        else:
            self._on_joyaxis_motion(joystick, "+"+axis, +value)
            self._on_joyaxis_motion(joystick, "-"+axis, -value)
    
    def on_joyhat_motion(self, joystick, hat_x, hat_y):
        self._on_joyaxis_motion(joystick, "+joyhat_x", +hat_x)
        self._on_joyaxis_motion(joystick, "-joyhat_x", -hat_x)
        self._on_joyaxis_motion(joystick, "+joyhat_y", +hat_y)
        self._on_joyaxis_motion(joystick, "-joyhat_y", -hat_y)

    def _on_joyaxis_motion(self, joystick, axis, value):
        state = (value > self.THRESHOLD)
        if state and not self.axis_states[axis]:
            assign_action("joystick", axis)
        self.axis_states[axis] = state

def reset_resting_positions(joystick):
    for axis in joystick.resting_positions:
        joystick.resting_positions[axis] = getattr(joystick, axis)

joysticks = pyglet.input.get_joysticks()
print(len(joysticks),"joysticks detected")
for joystick in joysticks:
    joystick.open()
    joystick.resting_positions = {}
    joystick.push_handlers(JoystickHandler())
    
recording_label = pyglet.text.Label('Placeholder Text',
                          font_name='Times New Roman',
                          font_size=36,
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')

def update_table():
    global batch
    # create new batch
    batch = pyglet.graphics.Batch()
    # grid
    for i in range(len(actions)+1):
        y = i*ROW_HEIGHT
        batch.add(2, pyglet.gl.GL_LINES, None, ('v2i', (0, y, window.width, y)),
                                      ('c4B', (255, 255, 255, 255) * 2))
    for i in range(10):
        x = ACTION_LABEL_WIDTH + i*KEY_LABEL_WIDTH
        batch.add(2, pyglet.gl.GL_LINES, None, ('v2i', (x, 0, x, window.height)),
                                      ('c4B', (255, 255, 255, 255) * 2))
        
    # labels
    for i, (action, description) in enumerate(actions):
        x = 0
        y = window.height-(i+3)*ROW_HEIGHT+3
        label = pyglet.text.Label(description,
                          font_name='Times New Roman',
                          font_size=FONT_SIZE,
                          x=x, y=y,
                          anchor_x='left', anchor_y='baseline',
                          batch=batch)

        for j, control_layer in enumerate(config["controls"]):
            event = control_layer.get(action, None)
            if event == None:
                continue
            x = ACTION_LABEL_WIDTH + j*KEY_LABEL_WIDTH
            text = str(event)
            color = (255,255,255,255)
            if event[0] == "key":
                text = key.symbol_string(event[1])
            if event[0] == "mouse":
                text = "M. "+mouse.buttons_string(event[1])
            if event[0] == "joystick":
                text = event[1]
            if event[0] == "scroll":
                text = " ".join(event)
            if event[0] == "error":
                text = event[1]
                color = (255,100,0,255)
            label = pyglet.text.Label(text,
                              font_name='Times New Roman',
                              font_size=FONT_SIZE,
                              x=x, y=y,
                              anchor_x='left', anchor_y='baseline',
                              color = color,
                              batch=batch)
    if changed_since_save:
        label = pyglet.text.Label("Save Changes",
                          font_name='Times New Roman',
                          font_size=FONT_SIZE,
                          x=0, y=window.height - ROW_HEIGHT//2,
                          anchor_x='left', anchor_y='top',
                          color = (255,100,0,255),
                          batch=batch)
        
    # update even on controller input
    window._legacy_invalid = True # otherwise Window won't update for some reason, another solution was to schedule a function that does nothing on main event loop

update_table()

print("please move analog inputs at least once before trying to assign them.\n (necessary to detect resting position)")

pyglet.app.run()

