#
# Copyright Tristam Macdonald 2008.
# Edited by Joram Brenz 2023
#
# Distributed under the Boost Software License, Version 1.0
# (see http://www.boost.org/LICENSE_1_0.txt)
#
# Found at: http://swiftcoder.wordpress.com/2008/12/19/simple-glsl-wrapper-for-pyglet/
#
# Note that there isn't anything restricting this class to use with Pyglet - a simple change to the import statement should allow it to be used with any setup based on OpenGL/ctypes. I hope someone finds this useful, and I would love to hear if you use it to make anything cool/interesting. 

from pyglet.gl import *
from ctypes import *
import collections

class Shader:
	# vert, frag and geom take arrays of source strings
	# the arrays will be concattenated into one string by OpenGL
	def __init__(self, vert = [], frag = [], geom = []):
		# create the program handle
		self.handle = glCreateProgram()
		# we are not linked yet
		self.linked = False

		# create the vertex shader
		self.createShader(vert, GL_VERTEX_SHADER)
		# create the fragment shader
		self.createShader(frag, GL_FRAGMENT_SHADER)
		# the geometry shader will be the same, once pyglet supports the extension
		# self.createShader(frag, GL_GEOMETRY_SHADER_EXT)

		# attempt to link the program
		self.link()

	def createShader(self, strings, type):
		count = len(strings)
		# if we have no source code, ignore this shader
		if count < 1:
			return
		# create the shader handle
		shader = glCreateShader(type)
		# convert the source strings into a ctypes pointer-to-char array, and upload them
		# this is deep, dark, dangerous black magick - don't try stuff like this at home!
		src = (c_char_p * count)(*strings)
		glShaderSource(shader, count, cast(pointer(src), POINTER(POINTER(c_char))), None)
		# compile the shader
		glCompileShader(shader)
		temp = c_int(0)
		# retrieve the compile status
		glGetShaderiv(shader, GL_COMPILE_STATUS, byref(temp))
		# if compilation failed, print the log
		if not temp:
			# retrieve the log length
			glGetShaderiv(shader, GL_INFO_LOG_LENGTH, byref(temp))
			# create a buffer for the log
			buffer = create_string_buffer(temp.value)
			# retrieve the log text
			glGetShaderInfoLog(shader, temp, None, buffer)
			# print the log to the console
			print(buffer.value)
		else:
			# all is well, so attach the shader to the program
			glAttachShader(self.handle, shader);
	
	def link(self):
		# link the program
		glLinkProgram(self.handle)
		temp = c_int(0)
		# retrieve the link status
		glGetProgramiv(self.handle, GL_LINK_STATUS, byref(temp))
		# if linking failed, print the log
		if not temp:
			# retrieve the log length
			glGetProgramiv(self.handle, GL_INFO_LOG_LENGTH, byref(temp))
			# create a buffer for the log
			buffer = create_string_buffer(temp.value)
			# retrieve the log text
			glGetProgramInfoLog(self.handle, temp, None, buffer)
			# print the log to the console
			print(buffer.value)
		else:
			# all is well, so we are linked
			self.linked = True
	
	def bind(self):
		# bind the program
		glUseProgram(self.handle)
	
	def unbind(self):
		# unbind whatever program is currently bound - not necessarily this program,
		# so this should probably be a class method instead
		glUseProgram(0)
	
	# upload a floating point uniform
	# this program must be currently bound
	def uniformf(self, name, *vals):
		# check there are 1-4 values
		if len(vals) in range(1, 5):
			# select the correct function
			{ 1 : glUniform1f, 2 : glUniform2f, 3 : glUniform3f, 4 : glUniform4f
			# retrieve the uniform location, and set
			}[len(vals)](glGetUniformLocation(self.handle, name), *vals)
	
	# upload an integer uniform
	# this program must be currently bound
	def uniformi(self, name, *vals):
		# check there are 1-4 values
		if len(vals) in range(1, 5):
			# select the correct function
			{ 1 : glUniform1i, 2 : glUniform2i, 3 : glUniform3i, 4 : glUniform4i
			# retrieve the uniform location, and set
			}[len(vals)](glGetUniformLocation(self.handle, name), *vals)
	
	# upload a uniform matrix
	# works with matrices stored as lists,
	# as well as euclid matrices
	def uniform_matrixf(self, name, mat):
		# obtian the uniform location
		loc = glGetUniformLocation(self.handle, name)
		# uplaod the 4x4 floating point matrix
		glUniformMatrix4fv(loc, 1, False, (c_float * 16)(*mat))

	def get_active_uniforms(self):
		active_uniforms = []
		Uniform = collections.namedtuple("Uniform", ["name", "type", "size"])

		count = c_int()
		glGetProgramiv(self.handle, GL_ACTIVE_UNIFORMS, byref(count));

		bufSize = 100
		length = GLsizei()
		size = GLint()
		type = GLenum()
		name = (GLchar * bufSize)()
		for i in range(count.value):
			glGetActiveUniform(self.handle, GLuint(i), bufSize, byref(length), byref(size), byref(type), name);
			assert length.value == len(name.value)
			active_uniforms.append(Uniform(name.value, type.value, size.value))
		return active_uniforms

	def get_uniformf(self, name, n=None):
		"""set n to read vector of size n
		if n is None, returns float directly instead of tuple with one float inside"""
		params = (GLfloat*(n or 1))()
		loc = glGetUniformLocation(self.handle, name)
		glGetUniformfv(self.handle, loc, params)
		if n is None:
			return tuple(params)[0]
		return tuple(params)
