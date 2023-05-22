class BlockWorld extends Map { get (key) { return super.get(""+key) }; set (key, value) { super.set(""+key, value); } }
var blocks = new BlockWorld();

class RNG { constructor (seed) { this.seed = seed }; next () { this.seed = hash(this.seed); return this.seed }; randint (lowerBound, upperBound) { var d = upperBound - lowerBound; return lowerBound + mod(this.next(), d+1); }; choice (options) { var i = mod(this.next(), options.length); return options[i]; }}; function hash (x) { /* https://stackoverflow.com/questions/664014/what-integer-hash-function-are-good-that-accepts-an-integer-hash-key/12996028#12996028 */ x = ((x >> 16) ^ x) * 0x45d9f3b; x &= 0xFFFFFFFF; x = ((x >> 16) ^ x) * 0x45d9f3b; x &= 0xFFFFFFFF; x = (x >> 16) ^ x; x &= 0xFFFFFFFF; return x }; function mod (x, d) { x %= d; if (x < 0) { x += d }; return x }
var random = new RNG(seed || 1);

// --------------------------- //

for (var x = -10; x <= 10; x = x + 1) {
	for (var z = -10; z <= 10; z = z + 1) {
		var material = random.choice(["GRASS","STONE","DIRT"]);
		blocks.set([x,0,z], material);
	}
}

// --------------------------- //

function terrain (position) {
	return blocks.get(position) || "AIR";
}
