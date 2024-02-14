
import sys, os
import json
import operator
from pprint import pprint
import math
from math import sin, cos

if __name__ == "__main__":
    sys.path.append(os.path.abspath(".."))
    print(sys.path)
    __package__ = "TPManager"

from voxelengine.modules.geometry import Vector

def face(vertices, texture, uvs):
	# flip v direction
	uvs = [(u,1-v) for u,v in uvs]

	xs, ys = zip(*uvs)
	if not (len(set(xs)) == len(set(ys)) == 2):
		#print("uv area has to be rectangular",uvs, xs, ys)
		pass
	x, *_, x_max = sorted(xs)
	y, *_, y_max = sorted(ys)
	w = x_max - x
	h = y_max - y
	
	# uvs in description.py format are always in the same order,
	# so we need to apply same permutation to vertices
	
	# find index of uv closest to (x,y), (x+w,y) and (x,y+h)
	i00,uv00 = min(enumerate(uvs), key=lambda iuv: (iuv[1][0]-x)**2 + (iuv[1][1]-y)**2)
	i10,uv10 = min(enumerate(uvs), key=lambda iuv: (iuv[1][0]-(x+w))**2 + (iuv[1][1]-y)**2)
	i01,uv01 = min(enumerate(uvs), key=lambda iuv: (iuv[1][0]-(x))**2 + (iuv[1][1]-(y+h))**2)

	d = (i10-i00)
	if (d%2 != 1):
		print("retrying mirroring decision with other neighbour")
		d = (i00-i01)
		if (d%2 != 1):
			print("could not decide mirroring")
			d = 1
	rotated_vertices = [
		vertices[(i*(d)+i00)%4]
		for i in range(len(vertices))
	]
	
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

def rotate_vertex_axis(v, axis, angle):
	"""Rodrigues rotation formula, angle in radians"""
	return cos(angle)*v + sin(angle)*axis.cross(v) + (1-cos(angle))*axis.dot(v)*axis

def rotate_vertex(vertex, rotation, origin):
	"""rotation: float[3] (x y and z rotation in degree)
	"""
	rx,ry,rz = rotation
	vertex -= Vector(origin)
	vertex = rotate_vertex_axis(vertex, Vector(1,0,0), math.radians(rx))
	vertex = rotate_vertex_axis(vertex, Vector(0,1,0), math.radians(ry))
	vertex = rotate_vertex_axis(vertex, Vector(0,0,1), math.radians(rz))
	vertex += origin
	return tuple(vertex)

def rotate_buffer(buf, rotation, origin):
	return [rotate_vertex(v, rotation, origin) for v in buf]

class BBModel(object):
	def __init__(self, fd):
		self.model = json.load(fd)

	def to_blockmodel(self):
		textures = [t["name"].rsplit(".",1)[0] for t in self.model["textures"]]
		resolution = self.model["resolution"]
		
		uv_scale = resolution["width"],resolution["height"]
		vertex_scale = 16,16,16
		vertex_offset = 0.5, 0, 0.5

		#pprint(self.model)

		faces = []
		for element in self.model["elements"]:
			if element["type"] == "mesh":
				if element.get("rescale",False) != False : print("unexpected value",element["rescale"],"for rescale")
				for facedata in element["faces"].values():
					if "texture" in facedata:
						texture = textures[facedata["texture"]]
					else:
						texture = "missing_texture"
					vertices = [element["vertices"][v] for v in facedata["vertices"]]
					if "rotation" in element:
						vertices = rotate_buffer(vertices, element["rotation"], element["origin"])
					vertices = scale_buffer(vertices, vertex_scale)
					vertices = offset_buffer(vertices, vertex_offset)
					uvs = [facedata["uv"][v] for v in facedata["vertices"]]
					uvs = scale_buffer(uvs, uv_scale)
					assert len(vertices) == len(uvs)
					if len(vertices) == 3:
						vertices.append(vertices[-1])
						uvs.append(uvs[-1])
					# undo strange order in bbmodel quads (are they maybe actually triangle stripes?)
					vertices = vertices[0],vertices[1],vertices[3],vertices[2]
					uvs = uvs[0],uvs[1],uvs[3],uvs[2]
					faces.append(face(vertices, texture, uvs))
			elif element["type"] == "cube":
				if element.get("autouv" ,0)     != 0     : print("unexpected value",element["autouv"] ,"for autouv" )
				if element.get("boxuv"  ,False) != False : print("unexpected value",element["boxuv"]  ,"for boxuv"  )
				if element.get("rescale",False) != False : print("unexpected value",element["rescale"],"for rescale")
				if element.get("rotation",False) != False : print("unexpected value",element["rotation"],"for rotation")
				pprint(element)
				x0,y0,z0 = element["from"]
				x1,y1,z1 = element["to"]
				for direction, facedata in element["faces"].items():
					if "texture" in facedata:
						texture = textures[facedata["texture"]]
					else:
						texture = "missing_texture"
					vertices = {
						# 00 10 11 01
						"down" : [(x0,y0,z1),(x1,y0,z1),(x1,y0,z0),(x0,y0,z0)],
						"east" : [(x1,y0,z0),(x1,y0,z1),(x1,y1,z1),(x1,y1,z0)],
						"north": [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0)],
						"south": [(x1,y0,z1),(x0,y0,z1),(x0,y1,z1),(x1,y1,z1)],
						"up"   : [(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)],
						"west" : [(x0,y0,z1),(x0,y0,z0),(x0,y1,z0),(x0,y1,z1)],
						}[direction]
					if "rotation" in element:
						vertices = rotate_buffer(vertices, element["rotation"], element["origin"])
					vertices = scale_buffer(vertices, vertex_scale)
					vertices = offset_buffer(vertices, vertex_offset)
					u0, v0, u1, v1 = facedata["uv"]
					uvs = [(u0,v0),(u1,v0),(u1,v1),(u0,v1)]
					r = int(facedata.get("rotation",0)//90)
					uvs = [uvs[(i+r)%len(uvs)] for i in range(len(uvs))]
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
	fname = os.path.join("..","..","features","bbmodeltest","data","fence","fence15.bbmodel")
	print(load_blockmodel(fname))
