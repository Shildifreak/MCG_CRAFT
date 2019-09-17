#* encoding: utf-8 *#

import sys, os
sys.path.append(os.path.join("lib","voxelengine","modules"))
import appdirs
import pyglet
from pyglet.window import key, mouse


configdir = appdirs.user_config_dir("MCGCraft","ProgrammierAG")
configfn = os.path.join(configdir,"clientsettings.py")
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
    ("for",  u"vorwärts laufen"),
    ("back", u"rückwärts laufen"),
    ("left", "nach links laufen"),
    ("right", "nach rechts laufen"),
    ("jump", u"hüpfen"),
    ("fly", "fliegen"),
    ("inv", u"inventar öffnen/schließen"),
    ("shift", u"ducken + sekundäre Mausfunktionen"),
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

@window.event
def on_key_press(s, modifiers):
    global symbol
    symbol = s
    try:
        label.text = next(a)
    except StopIteration:
        window.close()

def ablauf():
    keys = []
    for action, desc in actions:
        yield desc
        keys.append((symbol,action))
    config["controls"] = keys
    yield "Fertig!"
    with open(configfn,"w") as configfile:
        configfile.write(repr(config))
    print("saved")
    
a = ablauf()
label.text = next(a)

pyglet.app.run()

