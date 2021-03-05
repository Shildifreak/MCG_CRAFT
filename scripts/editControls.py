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

actions = [
    ("left_hand", u"Block abbauen / linke Hand"),
    ("right_hand", u"Block setzen / rechte Hand"),
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
    ("inv1", u"Inventarplatz 1 auswählen"),
    ("inv2", u"Inventarplatz 2 auswählen"),
    ("inv3", u"Inventarplatz 3 auswählen"),
    ("inv4", u"Inventarplatz 4 auswählen"),
    ("inv5", u"Inventarplatz 5 auswählen"),
    ("inv6", u"Inventarplatz 6 auswählen"),
    ("inv7", u"Inventarplatz 7 auswählen"),
    ("inv8", u"Inventarplatz 8 auswählen"),
    ("inv9", u"Inventarplatz 9 auswählen"),
    ("inv0", u"Inventarplatz 10 auswählen"),
    ]



window = pyglet.window.Window()
label = pyglet.text.Label('Placeholder text',
                          font_name='Times New Roman',
                          font_size=36,
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')
@window.event
def on_draw():
    window.clear()
    label.draw()

def assign_action(event_type, event_id):
    global event
    event = (event_type, event_id)
    print(event)
    try:
        label.text = next(a)
        window._legacy_invalid = True # otherwise Window won't update for some reason, another solution was to schedule a function that does nothing on main event loop
    except StopIteration:
        window.close()
    

@window.event
def on_key_press(key, modifiers):
    assign_action("key", key)

@window.event
def on_mouse_release(x, y, button, modifiers):
    assign_action("mouse", button)


class joystick_handlers(object):        
    THRESHOLD = 0.9
    def on_joybutton_press(joystick, button):
        assign_action("joystick", "button_%i"%button)

    def on_joyaxis_motion(joystick, axis, value):
        if getattr(joystick, axis+"_control").min == 0:
            # assume this is a trigger or so and values are mapped -1 ..1, so we want to map them back to 0 ..1
            value = (value + 1) / 2
        joystick_handlers._on_joyaxis_motion(joystick, "+"+axis, +value)
        joystick_handlers._on_joyaxis_motion(joystick, "-"+axis, -value)
    
    def on_joyhat_motion(joystick, hat_x, hat_y):
        joystick_handlers._on_joyaxis_motion(joystick, "+joyhat_x", +hat_x)
        joystick_handlers._on_joyaxis_motion(joystick, "-joyhat_x", -hat_x)
        joystick_handlers._on_joyaxis_motion(joystick, "+joyhat_y", +hat_y)
        joystick_handlers._on_joyaxis_motion(joystick, "-joyhat_y", -hat_y)

    def _on_joyaxis_motion(joystick, axis, value):
        state = (value > joystick_handlers.THRESHOLD)
        if state and not joystick.axis_states[axis]:
            assign_action("joystick", axis)
        joystick.axis_states[axis] = state


joysticks = pyglet.input.get_joysticks()
print(len(joysticks),"joysticks found")
for joystick in joysticks:
    joystick.axis_states = collections.defaultdict(bool)
    joystick.open()
    joystick.push_handlers(joystick_handlers)

def ablauf():
    keys = [
    ]
    for action, desc in actions:
        yield desc
        keys.append((event, action))
    config["controls"] = keys
    while True:
        yield "Speichern? (y/n)"
        if event[1] == key.Y:
            with open(configfn,"w") as configfile:
                configfile.write(repr(config))
            yield "gespeichert"
            break
        if event[1] == key.N:
            yield "nicht gespeichert"
            break
    
a = ablauf()
label.text = next(a)

pyglet.app.run()

