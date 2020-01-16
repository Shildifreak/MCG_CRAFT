from pprint import pprint
import os, math, functools, operator
import pygame

FACES = ("top","bottom","front","back","left","right")


class AutoIndex(dict):
	def __missing__(self, key):
		index = len(self)
		self[key] = index
		return index
		#return self[key] := index

def generate_desktop_version(normalized_universal_description, texture_directory, target_path):

	texture_index = AutoIndex()

	description = {"BLOCKS":[],"BLOCK_MODELS":[],"ENTITY_MODELS":{}}

	for blockname, blockdata in normalized_universal_description["BLOCKS"].items():
		
		transparent = blockdata["transparent"]
		texture_list = [(0, texture_index[blockdata["faces"][face]]) for face in FACES]
		icon = (0, texture_index[blockdata["icon"]])
		if icon in texture_list:
			icon_index = texture_list.index(icon)
		else:
			print("can't use icon thats not part of blocks textures in desktop version in",blockname)
			icon_index = 0
		block = blockname, transparent, icon_index, texture_list
		description["BLOCKS"].append(block)
	
	for blockmodelname, blockmodeldata in normalized_universal_description["BLOCK_MODELS"].items():
		transparent = blockmodeldata["transparent"]
		icon = (0, texture_index[blockmodeldata["icon"]])
		facecoordslist = []
		textcoordslist = []
		for face_category in FACES + ("inside",):
			facecoords = []
			textcoords = []
			for face in blockmodeldata["faces"][face_category]:
				corners, texture = face
				facecoords.append(functools.reduce(operator.add,corners))
				if isinstance(texture, str):
					texture_name, x, y, w, h = texture, 0, 0, 1, 1
				else:
					texture_name, x, y, w, h = texture
				y += texture_index[texture_name]
				textcoords.append((x,y,w,h))
			facecoordslist.append(facecoords)
			textcoordslist.append(textcoords)
		
		blockmodel = blockmodelname, transparent, icon, facecoordslist, textcoordslist
		description["BLOCK_MODELS"].append(blockmodel)
	
	description["ENTITY_MODELS"] = normalized_universal_description["ENTITY_MODELS"]

	TEXTURE_COUNT = 2**math.ceil(math.log2(len(texture_index)))
	description["TEXTURE_DIMENSIONS"] = (1, TEXTURE_COUNT)
	
	used_textures = set(texture_index.keys())
	existing_textures = set(texture_directory.list_textures())
	missing_textures = used_textures - existing_textures
	unused_textures = existing_textures - used_textures
	if missing_textures:
		print("MISSING TEXTURES:\n\t"+"\n\t".join(missing_textures))
	if unused_textures:
		print("unused_textures:\n\t"+"\n\t".join(unused_textures))
	output_size = (16,16)
	height = output_size[1]*TEXTURE_COUNT
	textures = pygame.surface.Surface((output_size[0], height), pygame.SRCALPHA)
	textures.fill((0,0,0,0))
	for name, index in texture_index.items():
		if name in missing_textures:
			continue
		t = texture_directory.read_texture(name)
		if t.get_size() != output_size:
			print("mismatched resolution, rescaling",name)
			t = pygame.transform.scale(t, output_size)
		textures.blit(t, (0, height - output_size[1]*(index+1)))

	if input("writing output to %s. Write Y to confirm: " % target_path) != "Y":
		print("task aborted by user request")
	else:
		with open(os.path.join(target_path, "description.py"), "w") as description_file:
			pprint(description, description_file, width = 200)
		pygame.image.save(textures, os.path.join(target_path, "textures.png"))




def generate_description():
	pass

def generate_texture_file():
	pass
