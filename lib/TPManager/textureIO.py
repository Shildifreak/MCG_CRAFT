import os
import json

import pygame


class TextureDirectory(object):
	def __init__(self, path):
		self.path = path
		self.reload()
	def reload(self):
		self.texture_files = {}
		self.material_files = {}
		assert os.path.isdir(self.path)
		for dirpath, dirnames, filenames in os.walk(self.path, topdown=True):
			if ".versions" in dirnames:
				dirnames.remove(".versions")
			for filename in filenames:
				if filename.endswith(".png"):
					texture_file = TextureFile(os.path.join(dirpath, filename))
					for name in texture_file.list_textures():
						assert name not in self.texture_files or print(name)
						if name.endswith(".material"):
							self.material_files[name] = texture_file
						else:
							self.texture_files[name] = texture_file
	def list_textures(self):
		return self.texture_files.keys()
	def read_texture(self, name):
		"""returns surface"""
		assert not name.endswith(".material")
		return self.texture_files[name].read_texture(name)
	def read_material(self, name):
		assert not name.endswith(".material")
		name += ".material"
		if name in self.material_files:
			return self.material_files[name].read_texture(name)
		return None
	def write_texture(self, name, surface):
		if name in self.texture_files:
			self.texture_files[name].write_texture(name, surface)
		else:
			raise NotImplementedError()

class TextureFile(object):
	def __init__(self, path):
		self.path = path
		self.description_path = os.path.splitext(self.path)[0] + ".json"
		self.reload()
	def reload(self):
		self.surface = pygame.image.load(self.path)
		if os.path.isfile(self.description_path):
			with open(self.description_path) as f:
				self.description = json.load(f)
		else:
			name = os.path.basename(os.path.splitext(self.path)[0])
			self.description = {"TEXTURE_SIZE" : self.surface.get_size(),
								"INDEX" : { name : (0,0), }, }
	def list_textures(self):
		return self.description["INDEX"].keys()
	def get_rect(self, name):
		kx, ky = self.description["TEXTURE_SIZE"]
		x, y = self.description["INDEX"][name]
		return (x*kx, y*ky, kx, ky)
	def read_texture(self, name):
		return self.surface.subsurface(self.get_rect(name))
	def write_texture(self, name, surface):
		# WARN IF .xcf FILE EXISTS!
		pass
	def get_name(self, position):
		reversed_index = {tuple(pos):name for name,pos in self.description["INDEX"].items()}
		return reversed_index.get(tuple(position), None)
	def set_name(self, position, new_name):
		old_name = self.get_name(position)
		if old_name:
			self.description["INDEX"].pop(old_name)
		if new_name:
			self.description["INDEX"][new_name] = position
		else:
			self.description["INDEX"].pop(new_name, None)
		# save changed index file
		if os.path.isfile(self.description_path):
			with open(self.description_path,"w") as f:
				json.dump(self.description, f, indent=4)
		else:
			print("can't set name, missing index file")
