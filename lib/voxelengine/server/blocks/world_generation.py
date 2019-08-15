
import imp
import random

def load_generator(generator_data):
	# creating the module
	generator_module = imp.new_module(generator_data["name"])

	# setting stuff up
	generator_module.seed = generator_data["seed"]
	generator_module.path = generator_data["path"]
	random.seed(generator_module.seed)

	# running module code
	code = compile(generator_data["code"], generator_data["path"], "exec")
	exec(code, generator_module.__dict__)

	# cleaning stuff up
	random.seed()
	if not hasattr(generator_module, "terrain") and not hasattr(generator_module, "terrain_js"):
		generator_module.terrain = empty_terrain
		generator_module.terrain_js = empty_terrain_js
	generator_module.init = with_seed(generator_module.init, generator_module.seed)

	# returning module
	return generator_module

def with_seed(init_function, seed):
	def new_init_function(world):
		random.seed(seed)
		init_function(world)
		random.seed()
	return new_init_function

def empty_terrain(position):
	return "AIR"

empty_terrain_js = """
function terrain(position) {
	return "AIR";
}
"""
