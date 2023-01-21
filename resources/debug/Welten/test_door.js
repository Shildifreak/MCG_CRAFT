class BlockWorld extends Map { get (key) { return super.get(""+key) }; set (key, value) { super.set(""+key, value); } }
var blocks = new BlockWorld();

var spawnpoint = [0, 3, 0];

// --------------------------- //

blocks.set([ 0, 0, 0], "DIAMANT");
blocks.set([ 0, 1, 0], "DOORBOTTOM");
blocks.set([ 0, 2, 0], "DOORTOP");

// --------------------------- //

function raw_terrain (position) {
	if (position[1] <= 0) {
		return "STONE";
	}
	return "AIR";
}

function terrain (position) {
	return blocks.get(position) || raw_terrain(position);
}
