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

def generate_web_version(normalized_universal_description, texture_directories, target_path):
	
	texture_index = AutoIndex()
	
	description = generate_description(texture_index, normalized_universal_description)
	textures = generate_textures_file(texture_index, texture_directories)
	
	os.makedirs(target_path, exist_ok=True)
	with open(os.path.join(target_path, "description.json"), "w") as description_file:
		json.dump(description, description_file)
	pygame.image.save(textures, os.path.join(target_path, "textures.png"))

def generate_description(texture_index, normalized_universal_description):
	description = {"blockDataArray":[],"blockIdByName":{},"icons":{},"blockModelData":{"vertexBuffer":[],"offsets":[0]},"properties":{"translucency":[],"renderbits":[]}}

	#	    -x   x      -y   y      -z   z     r g b a
	#	0x00040004, 0x00050003, 0x00040004, 0x00000000, # Grass
	
	assert texture_index["transparent"] == 0
	description["blockIdByName"]["AIR"] = 0
	description["blockDataArray"].extend([0,0,0,0])
	description["blockModelData"]["offsets"].append(0)
	description["properties"]["translucency"].append(255)
	description["properties"]["renderbits"].append(0x80)
	
	# BLOCKS
	blocknames = list(normalized_universal_description["BLOCKS"].keys())
	assert "AIR" not in blocknames
	for index_minus_one, blockname in enumerate(blocknames):
		index = index_minus_one + 1 #offset on index is due to AIR being index 0
		blockdata = normalized_universal_description["BLOCKS"][blockname]
		
		xFaces = (texture_index[blockdata["faces"]["left"  ]] << 16 << 4) + \
		         (texture_index[blockdata["faces"]["right" ]] <<  0 << 4)
		yFaces = (texture_index[blockdata["faces"]["bottom"]] << 16 << 4) + \
		         (texture_index[blockdata["faces"]["top"   ]] <<  0 << 4)
		zFaces = (texture_index[blockdata["faces"]["back"  ]] << 16 << 4) + \
		         (texture_index[blockdata["faces"]["front" ]] <<  0 << 4)
		fogColor = blockdata["fog_color"]
		fogColor = (fogColor[0] << 24) + (fogColor[1] << 16) + (fogColor[2] << 8) + (fogColor[3] << 0)
		blockDataArrayLine = [xFaces,yFaces,zFaces,fogColor]
		
		description["blockIdByName"][blockname] = index
		description["blockDataArray"].extend(blockDataArrayLine)
		
		icon = blockdata["icon"]
		description["icons"][blockname] = texture_index[icon]
	
	# ITEMS
	for itemname, itemdata in normalized_universal_description["ITEMS"].items():
		icon = itemdata["icon"]
		description["icons"][itemname] = texture_index[icon]
		
	# BLOCK MODELS
	blockmodelnames = blocknames + [n for n in normalized_universal_description["BLOCK_MODELS"].keys() if n not in blocknames] #same order as blocknames
	assert "AIR" not in blockmodelnames
	for index_minus_one, blockmodelname in enumerate(blockmodelnames):
		index = index_minus_one + 1 #offset on index is due to AIR being index 0
		blockmodeldata = normalized_universal_description["BLOCK_MODELS"][blockmodelname] #normalized universal description should also have a blockmodel for every normal block
		icon = blockmodeldata["icon"]
		description["icons"][blockmodelname] = texture_index[icon]

		for _, faces in blockmodeldata["faces"].items():
			for face in faces:
				vs, (texture_name, x, y, w, h) = face
				z = texture_index[texture_name]
				ts = ((x, y, z), (x+w, y, z), (x+w, y+h, z), (x, y+h, z))
				vs = tuple(tuple(coord-0.5 for coord in vertex) for vertex in vs)
				ds = [(*vn, *tn) for vn, tn in zip(vs, ts)]
				triangles = [*ds[0], *ds[1], *ds[2], *ds[2], *ds[3], *ds[0]]
				description["blockModelData"]["vertexBuffer"].extend(triangles)
		offsetNext = len(description["blockModelData"]["vertexBuffer"]) // 6
		description["blockModelData"]["offsets"].append(offsetNext)
		description["properties"]["translucency"].append(0xFF*bool(blockmodeldata["transparent"]))
		description["properties"]["renderbits"].append(0x80*bool(blockmodeldata["connecting"]))
		assert index == description["blockIdByName"].setdefault(blockmodelname, index)
				
	# just copy entity models for now
	description["ENTITY_MODELS"] = normalized_universal_description["ENTITY_MODELS"]

	description["TEXTURE_DIMENSIONS"] = (1, texture_index.texture_size())
	
	return description


def generate_textures_file(texture_index, texture_directories):
	TEXTURE_COUNT = texture_index.texture_size()
	
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
	output_size = tuple(map(max, *(texture_directory.read_texture(name).get_size()
	                               for name in texture_directory.list_textures() if name in used_textures
	                               for texture_directory in texture_directories)))
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
			m = texture_directory.read_material(name)
			if m and m.get_size() != output_size:
				print("mismatched resolution, rescaling",name+".material")
				m = pygame.transform.scale(m, output_size)
			t = apply_material(t, m)
			textures.blit(t, (0, output_size[1]*index))
	return textures


def apply_material(texture, material):
	width, height = texture.get_size()
	for y in range(height):
		for x in range(width):
			pos = (x,y)
			r, g, b, transparency = texture.get_at(pos)
			_, _, _, reflectivity = material.get_at(pos) if material else (0,0,0,255)
			a = min(transparency, reflectivity) & ~1;
			is_reflecting = transparency > reflectivity;
			a += is_reflecting;
			texture.set_at(pos, (r,g,b,a))
	
	return texture
