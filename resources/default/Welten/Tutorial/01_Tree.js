class BlockWorld extends Map { get (key) { return super.get(""+key) }; set (key, value) { super.set(""+key, value); } }
var blocks = new BlockWorld();

// --------------------------- //

blocks.set([0,0,0], "STONE");


// --------------------------- //

function terrain (position) {
	return blocks.get(position) || "AIR";
}
