import os, ast

import textureIO
from generate_desktop_version import generate_desktop_version
from generate_web_version     import generate_web_version


# find all universal version 1.0 directories
basepath = os.path.join("..","..","resources","texturepacks")
paths = os.listdir(basepath)

FACES = {"top","bottom","front","back","left","right"}

for relpath in paths:
	path = os.path.join(basepath, relpath)
	description_path = os.path.join(path, "description.py")
	if not os.path.isfile(description_path):
		continue

	print(path)
	with open(description_path) as description_file:
		description = ast.literal_eval(description_file.read())
	texture_directory = textureIO.TextureDirectory(path)
	
	# refine description
	description.setdefault("BLOCKS", {})
	for blockname, block in description["BLOCKS"].items():
		block.setdefault("transparent", False)
		block.setdefault("fog_color", (255, 255, 255, 0))
		block.setdefault("refraction_index", 1)
		block.setdefault("color_filter", ((1, 0, 0, 0),
										  (0, 1, 0, 0),
										  (0, 0, 1, 0),
										  (0, 0, 0, 1)))
		images = block.setdefault("faces", {})
		if {"all", "other"}.issubset(images):
			print('face keys "all" and "other" are doing the same, so using both is not very usefull', block)
		if FACES.issubset(images) and not {"all","other"}.isdisjoint(images):
			print('no need to use "all" or "other" if you have all the faces defined', block)
		images.setdefault("other", "missing_texture")
		images.setdefault("all", images["other"])
		for face in FACES:
			images.setdefault(face, images["all"])
		images.pop("other")
		images.pop("all")
		block.setdefault("icon", images["top"])
		if "missing_texture" in (block["icon"],*images.values()):
			print("missing some texture in", blockname)
	
	description.setdefault("BLOCK_MODELS", {})
	for blockmodelname, blockmodel in description["BLOCK_MODELS"].items():
		if not "icon" in blockmodel:
			blockmodel["icon"] = "missing_texture"
			print("missing icon in", blockmodelname)
		blockmodel.setdefault("transparent", True)
		faces = blockmodel.setdefault("faces", {})
		for face in (*FACES,"inside"):
			faces.setdefault(face, [])
	
	print("\nGenerating Desktop Version for Texturepack",relpath)
	try:
		generate_desktop_version(description, texture_directory, os.path.abspath(os.path.join(path,".versions","desktop")))
	except Exception as e:
		print(e)
	print("\nGenerating Web Version for Texturepack",relpath)
	try:
		generate_web_version    (description, texture_directory, os.path.abspath(os.path.join(path,".versions","web")))
	except Exception as e:
		print(e)
	
# create desktop and web version of those
