class BlockWorld extends Map { get (key) { return super.get(""+key) }; set (key, value) { super.set(""+key, value); } }
var blocks = new BlockWorld();

// --------------------------- //

function tree (x, y, z) {
	blocks.set([x+0, y+0, z+0], "STONE");
	blocks.set([x+0, y+1, z+0], "GRASS");
	blocks.set([x+0, y+2, z+0], "HOLZ" );
	blocks.set([x+0, y+3, z+0], "HOLZ" );
	blocks.set([x+0, y+4, z+0], "HOLZ" );
	blocks.set([x-1, y+4, z+0], "LAUB" );
	blocks.set([x+1, y+4, z+0], "LAUB" );
	blocks.set([x+0, y+4, z-1], "LAUB" );
	blocks.set([x+0, y+4, z+1], "LAUB" );
	blocks.set([x+0, y+5, z+0], "LAUB" );
}

tree(0,0,0);
tree(5,0,0);
tree(3,0,4);

// --------------------------- //

function terrain (position) {
	return blocks.get(position) || "AIR";
}
