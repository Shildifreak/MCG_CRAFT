
import os, sys, ast
import shutil

if __name__ == "__main__":
    sys.path.append(os.path.abspath(".."))
    __package__ = "TPManager"

from . import textureIO
from .generate_desktop_version import generate_desktop_version
from .generate_web_version     import generate_web_version
from .convert import load_blockmodel


FACES = {"top","bottom","front","back","left","right"}

class TP_Compiler(object):
	def __init__(self):
		self.description = {"ICONS":{},"BLOCKS":{},"BLOCK_MODELS":{},"ENTITY_MODELS":{},"SOUNDS":{}}
		self.texture_directories = []
		self.sound_files = {}
		self.model_files = {}
	
	def add_textures_from(self, path):
		self.texture_directories.append(textureIO.TextureDirectory(path))

		for dirpath, dirnames, filenames in os.walk(path, topdown=True):
			for filename in filenames:
				_, ext = os.path.splitext(filename)
				if ext in (".mp3", ".ogg", ".wav", ".m4a"):
					if filename in self.sound_files:
						print("multiple files for sound", filename)
					self.sound_files[filename] = os.path.join(dirpath, filename)
				if ext in (".bbmodel",):
					if filename in self.model_files:
						print("multiple files with name", filename)
					self.model_files[filename] = os.path.join(dirpath, filename)

		for dirpath, dirnames, filenames in os.walk(path, topdown=False):
			description_path = os.path.join(dirpath, "description.py")
			if os.path.isfile(description_path):
				self._add_description(description_path)

	def _add_description(self, description_path):
		with open(description_path) as description_file:
			description = ast.literal_eval(description_file.read())
		
		# refine description
		description.setdefault("BLOCKS", {})
		description.setdefault("BLOCK_MODELS", {})
		description.setdefault("ITEMS", {})
		description.setdefault("ENTITY_MODELS", {})
		description.setdefault("SOUNDS", {})
		description.setdefault("ICONS", {})
		
		for blockname, block in description["BLOCKS"].items():
			block.setdefault("transparent", False)
			block.setdefault("connecting", False)
			block.setdefault("fog_color", (255, 255, 255, 0))
			block.setdefault("material", "transparent" if block["transparent"] else "solid")
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
			block.setdefault("break_sound", "generic_block_broken.mp3")
			block.setdefault("place_sound", "generic_block_placed.mp3")
			# add blockmodel for blocks that don't have one
			if blockname not in description["BLOCK_MODELS"]:
				d = 0.01 if block["transparent"] else 0
				O, I = d, 1-d
				blockmodel = {"icon" : block["icon"],
							  "transparent": block["transparent"],
							  "connecting": block["connecting"],
							  "material": block["material"],
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
			# add sounds from blocks into the sound section
			if blockname+"_block_broken" not in description["SOUNDS"]:
				description["SOUNDS"][blockname+"_block_broken"] = block["break_sound"]
			if blockname+"_block_placed" not in description["SOUNDS"]:
				description["SOUNDS"][blockname+"_block_placed"] = block["place_sound"]
		
		# add blockmodels for items
		for itemname, itemdata in description["ITEMS"].items():
			icon = itemdata["icon"]
			blockmodel = {"icon" : icon,
						  "transparent": True,
						  "connecting": False,
						  "material": "transparent",
						  "fog_color": (255,255,255,0),
						  "faces": {"inside": [(((0,0,0.5),(0,1,0.5),(1,1,0.5),(1,0,0.5)),icon)],
								   }
						 }
			description["BLOCK_MODELS"][itemname] = blockmodel

		for blockmodelname, blockmodel in description["BLOCK_MODELS"].items():
			if "include" in blockmodel:
				include_model = load_blockmodel(self.model_files[blockmodel["include"]])
				for k,v in include_model.items():
					blockmodel.setdefault(k,v)
			if not "icon" in blockmodel:
				blockmodel["icon"] = "missing_texture"
				print("missing icon in", blockmodelname)
			blockmodel.setdefault("transparent", True)
			blockmodel.setdefault("connecting", False)
			blockmodel.setdefault("material", "transparent" if blockmodel["transparent"] else "solid")
			blockmodel.setdefault("fog_color", (255,255,255,0))
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
			# add icon to icons
			description["ICONS"][blockmodelname] = blockmodel["icon"]
		
		# update self.description
		for section in self.description:
			for name in description[section]:
				if name in self.description[section]:
					print("shadowing existing entry for",section,name)
				self.description[section][name] = description[section][name]
	
	def finish(self):
		if not self.texture_directories:
			raise RuntimeError("no texturepacks were found / added to TP_Compiler")


		# clean up missing and unused sounds
		existing_sound_files = set(self.sound_files.keys())
		used_sound_files = set(self.description["SOUNDS"].values())

		missing_sound_files = used_sound_files - existing_sound_files
		if missing_sound_files:
			print("MISSING SOUND FILES:\n\t"+"\n\t".join(missing_sound_files))
		for sound, sound_file in tuple(self.description["SOUNDS"].items()):
			if sound_file in missing_sound_files:
				self.description["SOUNDS"].pop(sound)

		unused_sound_files = existing_sound_files - used_sound_files
		if unused_sound_files:
			print("UNUSED SOUND FILES:\n\t"+"\n\t".join(unused_sound_files))
		for filename in unused_sound_files:
			self.sound_files.pop(filename)
	
	def generate_sound_folder(self, target_path):
		#print("\nGenerating Sound Folder for Texturepack")
		os.makedirs(target_path, exist_ok=True)
		for filename, src_path in self.sound_files.items():
			shutil.copyfile(src_path, os.path.join(target_path,filename))
	
	def save_to(self, path):
		self.finish()
		self.generate_sound_folder(os.path.join(path,"sounds"))
		generate_desktop_version(self.description, self.texture_directories, os.path.abspath(os.path.join(path,"desktop")))
		generate_web_version    (self.description, self.texture_directories, os.path.abspath(os.path.join(path,"web")))
	
# create desktop and web version of those


if __name__ == "__main__":
	
	paths = [
		os.path.abspath(os.path.join("..","..","features","essential","data")),
		#os.path.abspath(os.path.join("..","..","features","default","data")),
		os.path.abspath(os.path.join("..","..","features","bbmodeltest","data")),
		]
	print(paths)
	
	tp_compiler = TP_Compiler()
	for path in paths:
		tp_compiler.add_textures_from(path)

	print(tp_compiler.description["BLOCKS"].keys())
	
	tp_compiler.save_to("test")

