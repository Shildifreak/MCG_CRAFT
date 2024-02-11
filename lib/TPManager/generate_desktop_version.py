from pprint import pprint
import os, math, functools, operator
import pygame

FACES = ("top","bottom","front","back","left","right")


class AutoIndex(dict):
	def __missing__(self, key):
		if key == None:
			return self["missing_texture"]
		index = len(self)
		self[key] = index
		return index
		#return self[key] := index

def generate_desktop_version(normalized_universal_description, texture_directories, target_path):

	print("\nGenerating Desktop Version for Texturepack")

	texture_index = AutoIndex()

	description = {"BLOCK_MODELS":[],"ENTITY_MODELS":{},"SOUNDS":{}}
	
	for iconname, texturename in normalized_universal_description["ICONS"].items():
		transparent = True
		connecting = False
		material = "transparent"
		fog_color = (255,255,255,0)
		icon = (0, texture_index[texturename])
		facecoordslist = []
		textcoordslist = []
		fake_blockmodel = iconname, transparent, connecting, material, fog_color, icon, facecoordslist, textcoordslist
		description["BLOCK_MODELS"].append(fake_blockmodel)
	
	for blockmodelname, blockmodeldata in normalized_universal_description["BLOCK_MODELS"].items():
		transparent = blockmodeldata["transparent"]
		connecting = blockmodeldata["connecting"]
		material = blockmodeldata["material"]
		fog_color = blockmodeldata["fog_color"]
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
		
		blockmodel = blockmodelname, transparent, connecting, material, fog_color, icon, facecoordslist, textcoordslist
		description["BLOCK_MODELS"].append(blockmodel)
	
	description["ENTITY_MODELS"] = normalized_universal_description["ENTITY_MODELS"]

	description["SOUNDS"] = normalized_universal_description["SOUNDS"]

	TEXTURE_COUNT = 2**math.ceil(math.log2(len(texture_index)))
	description["TEXTURE_DIMENSIONS"] = (1, TEXTURE_COUNT)
	
	used_textures = set(texture_index.keys())
	existing_textures = set()
	for texture_directory in texture_directories:
		existing_textures.update(set(texture_directory.list_textures()))
	missing_textures = used_textures - existing_textures
	unused_textures = existing_textures - used_textures
	if missing_textures:
		print("MISSING TEXTURES:\n\t"+"\n\t".join(missing_textures))
	if unused_textures:
		print("unused_textures:\n\t"+"\n\t".join(unused_textures))
	#get output size
	output_size = tuple(map(max, zip(*(texture_directory.read_texture(name).get_size()
	                               for texture_directory in texture_directories
	                               for name in texture_directory.list_textures() if name in used_textures
	                              ))))
	print("TEXTURE_SIZE:", output_size)
	height = output_size[1]*TEXTURE_COUNT
	textures = pygame.surface.Surface((output_size[0], height), pygame.SRCALPHA)
	textures.fill((0,0,0,0))
	for texture_directory in texture_directories:
		existing_here = set(texture_directory.list_textures())
		for name in used_textures & existing_here:
			index = texture_index[name]
			t = texture_directory.read_texture(name)
			if t.get_size() != output_size:
				print("mismatched resolution, rescaling",name)
				t = pygame.transform.scale(t, output_size)
			textures.blit(t, (0, height - output_size[1]*(index+1)))
	
	os.makedirs(target_path, exist_ok=True)
	with open(os.path.join(target_path, "description.py"), "w") as description_file:
		pprint(description, description_file, width = 200)
	pygame.image.save(textures, os.path.join(target_path, "textures.png"))




def generate_description():
	pass

def generate_texture_file():
	pass
