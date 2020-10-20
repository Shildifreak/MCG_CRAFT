import os, math, functools, operator
import pygame
import json

FACES = ("top","bottom","front","back","left","right")


class AutoIndex(dict):
	def __missing__(self, key):
		index = len(self)
		assert index < (1 << 16)
		self[key] = index
		return index
		#return self[key] := index
	def texture_size(self):
		#return 2**math.ceil(math.log2(len(self)))
		return len(self)

def generate_web_version(normalized_universal_description, texture_directory, target_path):
	
	texture_index = AutoIndex()
	
	description = generate_description(texture_index, normalized_universal_description)
	textures = generate_textures_file(texture_index, texture_directory)
	
	with open(os.path.join(target_path, "description.json"), "w") as description_file:
		json.dump(description, description_file)
	pygame.image.save(textures, os.path.join(target_path, "textures.png"))

def generate_description(texture_index, normalized_universal_description):
	description = {"blockDataArray":[],"blockIdByName":{},"icons":{},"blockModelData":[],"blockModelIndices":{}}

	#	    -x   x      -y   y      -z   z     r g b a
	#	0x00040004, 0x00050003, 0x00040004, 0x00000000, # Grass
	
	assert texture_index["transparent"] == 0
	description["blockIdByName"]["AIR"] = 0
	description["blockDataArray"].extend([0,0,0,0])
	
	# BLOCKS
	for blockname, blockdata in normalized_universal_description["BLOCKS"].items():
		
		xFaces = (texture_index[blockdata["faces"]["left"  ]] << 16 << 4) + \
		         (texture_index[blockdata["faces"]["right" ]] <<  0 << 4)
		yFaces = (texture_index[blockdata["faces"]["bottom"]] << 16 << 4) + \
		         (texture_index[blockdata["faces"]["top"   ]] <<  0 << 4)
		zFaces = (texture_index[blockdata["faces"]["back"  ]] << 16 << 4) + \
		         (texture_index[blockdata["faces"]["front" ]] <<  0 << 4)
		fogColor = blockdata["fog_color"]
		fogColor = (fogColor[0] << 24) + (fogColor[1] << 16) + (fogColor[2] << 8) + (fogColor[3] << 0)
		blockDataArrayLine = [xFaces,yFaces,zFaces,fogColor]
		
		index = len(description["blockDataArray"])//4
		description["blockIdByName"][blockname] = index
		description["blockDataArray"].extend(blockDataArrayLine)
		
		icon = blockdata["icon"]
		description["icons"][blockname] = texture_index[icon]
	
	# ITEMS
	for itemname, itemdata in normalized_universal_description["ITEMS"].items():
		icon = itemdata["icon"]
		description["icons"][itemname] = texture_index[icon]
		
	# no block models for now, but icons
	for blockmodelname, blockmodeldata in normalized_universal_description["BLOCK_MODELS"].items():
		icon = blockmodeldata["icon"]
		description["icons"][blockmodelname] = texture_index[icon]

		blockModelIndexBegin = len(description["blockModelData"])
		for _, faces in blockmodeldata["faces"].items():
			for face in faces:
				vs, (texture_name, x, y, w, h) = face
				t = texture_index[texture_name]
				ts = ((t, x, y), (t, x+w, y), (t, x+w, y+h), (t, x, y+h))
				ds = [(*vn, *tn) for vn, tn in zip(vs, ts)]
				triangles = [*ds[0], *ds[1], *ds[2], *ds[2], *ds[3], *ds[0]]
				print(triangles)
				description["blockModelData"].extend(triangles)
		blockModelIndexEnd = len(description["blockModelData"])
		description["blockModelIndices"][blockmodelname] = (blockModelIndexBegin, blockModelIndexEnd)
				
	# no entity models for now

	description["TEXTURE_DIMENSIONS"] = (1, texture_index.texture_size())
	
	return description


def generate_textures_file(texture_index, texture_directory):
	TEXTURE_COUNT = texture_index.texture_size()
	
	used_textures = set(texture_index.keys())
	existing_textures = set(texture_directory.list_textures())
	missing_textures = used_textures - existing_textures
	unused_textures = existing_textures - used_textures
	if missing_textures:
		print("MISSING TEXTURES:\n\t"+"\n\t".join(missing_textures))
	if unused_textures:
		print("unused_textures:\n\t"+"\n\t".join(unused_textures))
	#get output size
	output_size = tuple(map(max, *(texture_directory.read_texture(name).get_size() for name in texture_index if name not in missing_textures)))
	print("TEXTURE_SIZE:", output_size)
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
		textures.blit(t, (0, output_size[1]*index))
	return textures
