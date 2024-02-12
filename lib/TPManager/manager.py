"""

Dinge die aufgelistet werden sollten:
	Namen die im einen oder anderen TP nicht enthalten sind
	Namen die in beiden TPs existieren aber unterschiedlichen Inhalt haben
	Orte / Kacheln die keinen Namen / kein Indexfile haben

Fenster zum Auswählen von Einzelbildern und Bereichen, denen man Namen geben kann

name: some name (suggest names of images that exist but are not linked)
<- replace left with right
-> replace right with left

toggle_view, rename, replace left, replace right

"""

#TD_PATHS = ["../test%i"%i for i in range(2)]
#TF_PATH  = "../test0/chest.png"

import time
_input = input
def input(prompt=""):
	"""console can buffer input from before and send it before
	the user gets a chance to enter the real thing"""
	while True:
		t0 = time.time()
		i = _input(prompt)
		t1 = time.time()
		if t1 - t0 > 0.1:
			return i
	

import os
BASE_PATH = os.path.join("..","..","features")

TD_PATHS = [
	os.path.join(BASE_PATH, "default",        "textures"),
	os.path.join(BASE_PATH, "weihnachtsdeko", "textures"),
#	os.path.join("..","..","tests","old_texturepacks","default_stable"),
]
TF_PATH  = os.path.join(TD_PATHS[0], "textures.png")

#TD_PATHS = ["../basic_colors"]
#TF_PATH = "../basic_colors/textures.png"

import pygame
import itertools

from textureIO import TextureFile, TextureDirectory

def compare_surfaces(name, td_a, td_b):
	t0 = td_a.read_texture(name)
	t1 = td_b.read_texture(name)
	if t0.get_size() != t1.get_size():
		return False
	
	for x in range(t0.get_width()):
		for y in range(t0.get_height()):
			c1 = t0.get_at((x,y))
			c2 = t1.get_at((x,y))
			if c1 != c2:
				if (c1[3] or c2[3]): # if booth were fully transparent the color wouldn't matter
					return False
	return True

def compare():
	global missing, different
	tns = [set(td.list_textures()) for td in tds]
	all_names = set.union(*tns)
	missing = set()
	different = set()
	for name in all_names:
		td_yes = set()
		td_no = set()
		for i, td in enumerate(tds):
			if name in tns[i]:
				td_yes.add(td)
			else:
				td_no.add(td)
		if td_no:
			missing.add(name)
		for td_a, td_b in itertools.combinations(td_yes,2):
			if compare_surfaces(name, td_a, td_b) == False:
				different.add(name)
				break
	return missing, different

SCALE = 4
mosaik = TextureFile(TF_PATH)
tds = [TextureDirectory(path) for path in TD_PATHS]
IMAGE_SIZE = SCALE * 16

missing = set()
different = set()
selected_position = None
selected_name = None

print(compare())

window_size = (mosaik.surface.get_width()*SCALE, mosaik.surface.get_height()*SCALE)
window = pygame.display.set_mode(window_size)

def select(position):
	global selected_position, selected_name
	if position == selected_position:
		selected_position = None
	else:
		selected_position = position
	if selected_position:
		selected_name = mosaik.get_name(position)
	else:
		selected_name = None
	print(selected_position, selected_name)
	update()

def rename():
	if not selected_position:
		print("Please select a position to rename.")
		return
	new_name = input("New name for position %s of %s: " %(selected_position, mosaik.path))
	mosaik.set_name(selected_position, new_name)
	reload()

def update():
	#draw
	scaled_mosaik = pygame.transform.scale(mosaik.surface, window_size)
	window.fill((0,0,0))
	window.blit(scaled_mosaik,(0,0))
	for name in mosaik.list_textures():
		if name in missing:
			color = (200,0,255)
		elif name in different:
			color = (255,255,0)
		else:
			color = (0,255,0)
		rect = tuple( x*SCALE for x in mosaik.get_rect(name) )
		width = 3
		pygame.draw.rect(window, color, rect, width)
	if selected_position:
		color = (255,0,0)
		rect = (selected_position[0]*IMAGE_SIZE, selected_position[1]*IMAGE_SIZE, IMAGE_SIZE, IMAGE_SIZE)
		width = 2
		pygame.draw.rect(window, color, rect, width)
update()

def reload():
	for td in tds:
		td.reload()
	mosaik.reload()
	compare()
	
	
	update()

HELPTEXT = """
F1: Display help text
F2: Rename Tile (r)
F5: Reload
Arrow Keys: Move Cursor
"""

ende = False
while not ende:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			ende = True
		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				pos = event.pos[0] // IMAGE_SIZE, event.pos[1] // IMAGE_SIZE
				select(pos)
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_F1:
				print(HELPTEXT)
			if event.key in (pygame.K_r, pygame.K_F2):
				rename()
			if event.key == pygame.K_F5:
				reload()
			if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
				if not selected_position:
					selected_position = (0,0)
				x = selected_position[0] - (event.key == pygame.K_LEFT) + (event.key == pygame.K_RIGHT)
				y = selected_position[1] - (event.key == pygame.K_UP) + (event.key == pygame.K_DOWN)
				select((x,y))
				
	pygame.display.update()

pygame.quit()
