var spawnpoint = [0,5,0];

class BlockWorld extends Map { get (key) { return super.get(""+key) }; set (key, value) { super.set(""+key, value); } }
var blocks = new BlockWorld();

// --------------------------- //

for (var x = -10; x <= 10; x = x + 1) {
for (var z = -10; z <= 10; z = z + 1) {
	for (var y = -10; y < 0; y = y + 1) {
		blocks.set([x,y,z], "DIRT");
	}
	blocks.set([x,0,z], "GRASS");
}}

function lake (x,y,z,r) {
	for (var dx = -r; dx <= r; dx++) {
	for (var dz = -r; dz <= r; dz++) {
	for (var dy = -r; dy <= 0; dy++) {
		if (dx*dx + dy*dy + dz*dz < r*r) {
			blocks.set([x+dx,y+dy,z+dz], "WATER");
		}
	}}}
}
lake(-5, 0,-2, 5);
lake( 5, 2, 3, 5);

// --------------------------- //

function terrain (position) {
	return blocks.get(position) || "AIR";
}
