class BlockWorld extends Map { get (key) { return super.get(""+key) }; set (key, value) { super.set(""+key, value); } }
var blocks = new BlockWorld();

// --------------------------- //

blocks.set([ 0, 0, 0], "STONE");
blocks.set([ 0, 1, 0], "GRASS");
blocks.set([ 0, 2, 0], "HOLZ" );
blocks.set([ 0, 3, 0], "HOLZ" );
blocks.set([ 0, 4, 0], "HOLZ" );
blocks.set([-1, 4, 0], "LAUB" );
blocks.set([ 1, 4, 0], "LAUB" );
blocks.set([ 0, 4,-1], "LAUB" );
blocks.set([ 0, 4, 1], "LAUB" );
blocks.set([ 0, 5, 0], "LAUB" );


// --------------------------- //

function terrain (position) {
	return blocks.get(position) || "AIR";
}
