
import imp


def load_generator(generator_data):
	generator_module = imp.new_module(generator_data["name"])
	generator_module.seed = generator_data["seed"]
	generator_module.path = generator_data["path"]
	exec(generator_data["code"], generator_module.__dict__)

	if not hasattr(generator_module, "terrain") and not hasattr(generator_module, "terrain_js"):
		generator_module.terrain = empty_terrain
		generator_module.terrain_js = empty_terrain_js

	return generator_module



def empty_terrain(self, position):
	return "AIR"

empty_terrain_js = """
function terrain(position) {
	return "AIR";
}
"""
