# MCG CRAFT #

![Screenshot](http://mcgcraft.de/screenshots/screenshot_mcgcraft_small.png)

- multiplayer
- easily create new features using plugins
- arbitrary high (and deep) worlds
- powerfull event system
- open source
- written in Python and JavaScript

## Idea, Goals and History of the Project

MCGCraft was started in 2016 by students of the Marie Curie Gymnasium wanting to recreate the famous game minecraft.

We now have a voxel based game engine that can be used for teaching the basics of programming.  
A plugin approach allows students to create and later combine their own versions of the game.
These so called resource packs allow to add
- new worlds with custom terrain generation
- textures
- 3D models for blocks and entities
- behaviour for blocks and entities

As part of making MCGCraft more accessible, some features can be tried online at http://mcgcraft.de  
This includes:
- MCGCraft WebClient - a fully functional MCGCraft client running javascript and webgl that can be used to join existing games (including custom local ones)
- Demo Server
- Editor with live preview for JavaScript based terrain generation

In the future we hope to add lots of Tutorials and maybe even an environment for collaborative coding and running mcgcraft servers.


## Installation

### Security Concerns
Keep in mind that this is the result of a school project.  
As stated in the licence agreement you are using this software at your own risk.  

To minimize your risk:
- **only use resource packs you trust!** (included code will be executed as part of the game)
- **only connect to servers you trust!** (world generation code is sandboxed, but still)
- **always run behind a firewall**

### Requirements
python >= 3.8 (Python 3.8 is currently used for development, older versions are not supported but may work, newer versions should work if not feel free to open an issue.)  
pygame needs to be installed seperately and is available via pip or from pygame.org  
py_mini_racer binaries may only be compatible with 64bit systems  

### Steps
1. Install Python from python.org -	make sure to select pip and tkinter if the option is there
2. Run python -m pip install pygame - on linux you may need to change python to python3 you may want to add --user to the options
3. If your python didn't come with tkinter, on linux get python3-tk or pip install tk
3. Download MCGCraft from github.com/Shildifreak/MCG_CRAFT - you can either click Code > Download Zip or clone the repository
4. In the main MCGCraft Directory run launcher.py

### tldr; youtube video (German)
https://www.youtube.com/watch?v=ND9UUnEKVWU

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

## Documentation

There is currently a severe lack of documentation.
We need:
- complete documentation of the code
- architecture overview diagrams (modules, client-server, configuration, resource-packs, ...)
- tutorials (terrain generation, textures, models, behaviour)
