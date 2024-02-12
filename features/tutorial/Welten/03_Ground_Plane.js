class BlockWorld extends Map { get (key) { return super.get(""+key) }; set (key, value) { super.set(""+key, value); } }
var blocks = new BlockWorld();

// --------------------------- //

for (var x = -10; x <= 10; x = x + 1) {
	for (var z = -10; z <= 10; z = z + 1) {
		blocks.set([x,0,z], "GRASS");
	}
}

// --------------------------- //

function terrain (position) {
	return blocks.get(position) || "AIR";
}
