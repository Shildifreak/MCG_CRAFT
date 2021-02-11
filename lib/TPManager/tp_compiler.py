
import os, sys, ast

if __name__ == "__main__":
    sys.path.append(os.path.abspath(".."))
    __package__ = "TPManager"

from . import textureIO
from .generate_desktop_version import generate_desktop_version
from .generate_web_version     import generate_web_version



FACES = {"top","bottom","front","back","left","right"}

class TP_Compiler(object):
	def __init__(self):
		self.description = {"BLOCKS":{},"BLOCK_MODELS":{},"ITEMS":{},"ENTITY_MODELS":{}}
		self.texture_directories = []
	
	def add_textures_from(self, path):
		description_path = os.path.join(path, "description.py")
		if not os.path.isfile(description_path):
			print("textures are missing description",description_path)
			return

		with open(description_path) as description_file:
			description = ast.literal_eval(description_file.read())
		self.texture_directories.append(textureIO.TextureDirectory(path))
		
		# refine description
		description.setdefault("BLOCKS", {})
		description.setdefault("BLOCK_MODELS", {})
		description.setdefault("ITEMS", {})
		description.setdefault("ENTITY_MODELS", {})
		
		for blockname, block in description["BLOCKS"].items():
			block.setdefault("transparent", False)
			block.setdefault("connecting", False)
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
			# add blockmodel for blocks that don't have one
			if blockname not in description["BLOCK_MODELS"]:
				d = 0.01 if block["transparent"] else 0
				O, I = d, 1-d
				blockmodel = {"icon" : block["icon"],
							  "transparent": block["transparent"],
							  "connecting": block["connecting"],
							  "faces": {"top"   : [(((O,I,I),(I,I,I),(I,I,O),(O,I,O)),images["top"   ])],
										"bottom": [(((I,O,I),(O,O,I),(O,O,O),(I,O,O)),images["bottom"])],
										"front" : [(((O,O,I),(I,O,I),(I,I,I),(O,I,I)),images["front" ])],
										"back"  : [(((I,O,O),(O,O,O),(O,I,O),(I,I,O)),images["back"  ])],
										"left"  : [(((O,O,O),(O,O,I),(O,I,I),(O,I,O)),images["left"  ])],
										"right" : [(((I,O,I),(I,O,O),(I,I,O),(I,I,I)),images["right" ])],
										"inside": [],
									   }
							 }
				if block["transparent"]:
					for face in FACES:
						blockmodel["faces"]["inside"].extend(blockmodel["faces"].pop(face))
				description["BLOCK_MODELS"][blockname] = blockmodel
		
		for blockmodelname, blockmodel in description["BLOCK_MODELS"].items():
			if not "icon" in blockmodel:
				blockmodel["icon"] = "missing_texture"
				print("missing icon in", blockmodelname)
			blockmodel.setdefault("transparent", True)
			blockmodel.setdefault("connecting", False)
			faces = blockmodel.setdefault("faces", {})
			for face in (*FACES,"inside"):
				facedata = faces.get(face, [])
				new_facedata = []
				for corners, texture in facedata:
					if isinstance(texture, str):
						texture = (texture,)
					texture = texture + ("missing_texture", 0, 0, 1, 1)[len(texture):]
					new_facedata.append((corners, texture))
				faces[face] = new_facedata
		
		# update self.description
		for section in description:
			for name in description[section]:
				if name in self.description[section]:
					print("overwriting existing entry for",section,name)
				self.description[section][name] = description[section][name]
	
	def save_to(self, path):
		print("\nGenerating Desktop Version for Texturepack")
		if not self.texture_directories:
			raise RuntimeError("no texturepacks were found / added to TP_Compiler")
		generate_desktop_version(self.description, self.texture_directories, os.path.abspath(os.path.join(path,"desktop")))
		generate_web_version    (self.description, self.texture_directories, os.path.abspath(os.path.join(path,"web")))
	
# create desktop and web version of those


if __name__ == "__main__":
	
	path = os.path.join("..","..","resources","default","textures")
	path = os.path.abspath(path)
	print(path)
	
	tp_compiler = TP_Compiler()
	tp_compiler.add_textures_from(path)
	
	tp_compiler.save_to("test")

