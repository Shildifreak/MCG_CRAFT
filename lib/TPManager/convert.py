
import sys, os
import json
import operator
from pprint import pprint

def face(vertices, texture, uvs):
	xs, ys = zip(*uvs)
	if not (len(set(xs)) == len(set(ys)) == 2):
		print("uv area has to be rectangular",uvs, xs, ys)
	x, *_, x_max = sorted(xs)
	y, *_, y_max = sorted(ys)
	w = x_max - x
	h = y_max - y
	
	rotated_vertices = []
	uv00,uv01,uv10,uv11 = sorted(uvs)
	for uv in [uv00,uv10,uv11,uv01]:
		i = uvs.index(uv)
		v = vertices[i]
		rotated_vertices.append(v)
	
	rect = (x,y,w,h)
	if rect == (0,0,1,1):
		return (rotated_vertices, texture)
	else:
		return (rotated_vertices, (texture, *rect))

def scale_buffer(buf, scale):
	scaled_buf = []
	for v in buf:
		scaled_buf.append(tuple(map(operator.truediv, v, scale)))
	return scaled_buf

def offset_buffer(buf, offset):
	offset_buf = []
	for v in buf:
		offset_buf.append(tuple(map(operator.add, v, offset)))
	return offset_buf

class BBModel(object):
	def __init__(self, fd):
		self.model = json.load(fd)

	def to_blockmodel(self):
		textures = [t["name"].rsplit(".",1)[0] for t in self.model["textures"]]
		resolution = self.model["resolution"]
		
		uv_scale = resolution["width"],resolution["height"]
		vertex_scale = 16,16,16
		vertex_offset = 0.5, 0, 0.5

		pprint(self.model)

		faces = []
		for element in self.model["elements"]:
			if element["type"] == "mesh":
				for facedata in element["faces"].values():
					if "texture" in facedata:
						texture = textures[facedata["texture"]]
					else:
						texture = "missing_texture"
					vertices = [element["vertices"][v] for v in facedata["vertices"]]
					vertices = scale_buffer(vertices, vertex_scale)
					vertices = offset_buffer(vertices, vertex_offset)
					uvs = [facedata["uv"][v] for v in facedata["vertices"]]
					uvs = scale_buffer(uvs, uv_scale)
					faces.append(face(vertices, texture, uvs))
			else:
				print("BBModel include: unsupported element type",element["type"])

		return {"faces":{"inside":faces}}

def load_blockmodel(fname):
	with open(fname) as f:
		if fname.endswith(".bbmodel"):
			model = BBModel(f)
		else:
			raise ValueError("Unsupported filetype for blockmodel",fname)
	return model.to_blockmodel()
	
if __name__ == "__main__":
	fname = os.path.join("..","..","features","bbmodeltest","data","EmeraldStairs.bbmodel")
	print(load_blockmodel(fname))
