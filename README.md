# MCG CRAFT #

![Screenshot](http://mcgcraft.de/screenshots/screenshot_mcgcraft_small.png)

- multiplayer
- easily create new features using Python and JavaScript plugins
- arbitrary high (and deep) worlds
- powerful event system
- 3D tag based index for block and entity selection

## Idea, Goals and History of the Project

MCGCraft was started in 2016 by students of the Marie Curie Gymnasium wanting to recreate the famous game minecraft.

We now have a voxel based game engine that can be used for teaching the basics of programming.  
A plugin approach allows students to create and later combine their own versions of the game.
These so called feature packs allow to add
- new worlds with custom terrain generation
- textures
- 3D models for blocks and entities
- behaviour for blocks and entities

As part of making MCGCraft more accessible, some features can be tried online at http://mcgcraft.de  
This includes:
- [Demo Server](http://play.mcgcraft.de) - try MCGCraft for yourself (on an unmoderated public multiplayer server with terrible latency)
- [MCGCraft WebClient](http://mcgcraft.de/webclient/) - a fully functional MCGCraft client running javascript and webgl
- [Tech Demo](https://mcgcraft.de/webclient/techdemo_2/) - standalone demo of the raytracing rendering used in the webclient
- [TP Viewer](http://mcgcraft.de/webclient/tools/tp_viewer/) - inspect the texture pack provided by an MCGCraft server
- [Terrain Editor](https://mcgcraft.de/webclient/latest/terraintest/) - edit and live preview JavaScript based terrain generation

In the future we hope to add lots of [Tutorials](https://mcgcraft.de/youtube) and maybe even an environment for collaborative coding and running mcgcraft servers.


## Getting Started

### ⚠ Security Concerns ⚠
Keep in mind that this is the result of a school project.  
As stated in the licence agreement you are using this software at your own risk.  

To minimize your risk:
- **only use feature packs you trust!** (included code will be executed as part of the game)
- **only connect to servers you trust!** (world generation code is supposedly sandboxed, but still)
- **always run behind a firewall**

### Requirements / Dependencies
MCGCRAFT uses the following external programs and libraries. For step by step installation instructions go on to the section below.

**Python** - [python.org](python.org)  
Python3.10 is currently used for development. Older versions are not tested but may still work. Newer versions should work, if not feel free to open an issue.

**Pygame** - [pygame.org](pygame.org)  
Pygame is used by the server for image manipulation when compiling texture packs.

**PyGlet** - [github.com/pyglet/pyglet](github.com/pyglet/pyglet)  
Pyglet is the OpenGL library used for the MCGCraft Desktop Client.  
MCGCraft comes with PyGlet built in. (for now)

**PyMiniRacer** - [github.com/sqreen/PyMiniRacer](github.com/sqreen/PyMiniRacer)  
MiniRacer is a python wrapper for the V8 JavaScript Engine. We use it to evaluate the terrain function. (Which is written in JS so we can have a webclient.)  
MCGCraft comes with binaries for PyMiniRacer built in, but they are probably **only compatible with 64bit systems**.


### Installation (Windows)
[video guide (German)](https://www.youtube.com/watch?v=ND9UUnEKVWU)
1. Install latest Python from [python.org](https://www.python.org/downloads/) -	make sure pip and tkinter are selected in the installation dialog as well as the add python to PATH option
2. Open a command line and run `python -m pip install pygame` to install pygame

### Installation (Linux Debian/Ubuntu)
1. Install Python `apt install python3`
2. Install Pygame `apt install python3-pygame` or `python3 -m pip install pygame`
3. Install Tkinter `apt install python3-tk` or `python3 -m pip install tk`

### Installation (Final Steps)
4. Download MCGCraft from github.com/Shildifreak/MCG_CRAFT
   1. you can either click Code > Download Zip
   2. or install git and clone the repository (required for update function in the launcher to work)
5. In the main MCGCraft directory run launcher.py

## Client Features Comparison

| Categorie      | Feature                    | Desktop Client      | Web Client             |
|----------------|----------------------------|---------------------|------------------------|
|                |                            |                     |                        |
| Rendering      |                            | classic             | raytracing hybrid      |
|                | Opaque Full Blocks         | ✔                   | ✔                      |
|                | 3D Blockmodels             | ✔                   | ✔                      |
|                | transparent Pixels         | ✔                   | ✔                      |
|                | Semitransparency           | ❌                  | ✔ (Blocks only)        |
|                | Reflections                | ❌                  | ✔ (Blocks only)        |
|                | Fog Blocks                 | ❌                  | ✔                      |
|                | Entities                   | ✔                   | ✔                      |
|                |                            |                     |                        |
| HUD            | In Game HUD                | ✔                   | ✔                      |
|                | Drag & Drop Items          | ✔                   | ✔                      |
|                |                            |                     |                        |
| Chat & Debug   | Chat                       | ✔                   | ✔                      |
|                | Coordinate Display         | ✔                   | ✔                      |
|                | FPS Display                | ✔ (toggle with F3)  | ✔                      |
|                |                            |                     |                        |
| Inputs         | Controller Support         | ✔                   | ❌                     |
|                | Configurable Keybindings   | ✔                   | ❌                     |
|                | Gyroscope Camera Control   | ❌                  | ✔ (on some devices)    |
|                | Touch Onscreen Controls    | ❌                  | ❌                     |
|                |                            |                     |                        |
| Technical      | use terrain hints          | ✔                   | ❌                     |
|                | uses same code as server   | ✔                   | ❌                     |
|                | multicore support          | ❌                  | ✔                      |
|                | ambient occlusion lighting | ✔ (toggle with F4)  | ✔                      |
|                | join local or remote games | ✔                   | ✔                      |
|                | secure websocket support   | ❌                  | ✔ (but server doesn't) |

## Documentation

There is currently a severe lack of documentation.
We need:
- complete documentation of the code
- architecture overview diagrams (modules, client-server, configuration, resource-packs, ...)
- tutorials (terrain generation, textures, models, behaviour)
