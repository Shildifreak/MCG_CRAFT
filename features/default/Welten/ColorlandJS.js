
const spawnpoint = [0,20,0];
const n = 50;  // 1/2 width and height of world

// things that should really just be imported from somewhere common

function hash (x) {
    // https://stackoverflow.com/questions/664014/what-integer-hash-function-are-good-that-accepts-an-integer-hash-key/12996028#12996028
    x = ((x >> 16) ^ x) * 0x45d9f3b;
    x &= 0xFFFFFFFF;
    x = ((x >> 16) ^ x) * 0x45d9f3b;
    x &= 0xFFFFFFFF;
    x = (x >> 16) ^ x;
    x &= 0xFFFFFFFF;
    return x;
}

function mod (x, d) {
	x %= d;
	if (x < 0) { x += d };
	return x;
}

class RNG {
	constructor (seed) {
		this.seed = seed;
	}

	next () {
		this.seed = hash(this.seed);
		return this.seed;
	}

	randint (lowerBound, upperBound) {
		var d = upperBound - lowerBound;
		return lowerBound + mod(this.next(), d+1);
	}

	choice (options) {
		var i = mod(this.next(), options.length);
		return options[i];
	}
}

var random;
if (Number.isInteger(seed) && (seed >= 0)) {
	random = new RNG(seed || 1);
}
else {
	random = new RNG(seed*(1<<30) || 1);
}

class BlockMap extends Map {
	get (position) {
		var key = JSON.stringify(position);
		return super.get(key);
	}
	
	set (position, value) {
		var key = JSON.stringify(position);
		super.set(key, value);
	}
}

const MapProxyHandler = {
	get : function (obj, key) {
		return obj.get(key);
	},
	set : function (obj, key, value) {
		obj.set(key, value);
		return true;
	},
};

var welt = {
	blocks : new Proxy(new BlockMap(), MapProxyHandler),
};

// init world

function init() {
	//
	// Initialize the world by placing all the blocks.
	//
	const o = n - 10; // until where to place (center of) hills and trees

	for (let i = 0; i < 100; i++) {
		let a = random.randint(-n, n);
		let b = random.randint(-n, n);
		welt.blocks[[a, -1, b]] = "TNT";
	}

	// generate the hills randomly
	for (let i = 0; i < 10; i++) {
		let a = random.randint(-o, o); // x position of the hill
		let b = random.randint(-o, o); // z position of the hill
		let c = -1;                    // base of the hill
		let h = random.randint(3, 6);  // height of the hill
		let s = random.randint(4, 8);  // 2 * s is the side length of the hill
		let d = 1;                     // how quickly to taper off the hills
		let t = random.choice(["HELLBLAU", "BRAUN", "GRAU", "ROT"]);
		for (let y = c; y < c+h; y++) {
			for (let x = a - s; x < a + s + 1; x++) {
				for (let z = b - s; z < b + s + 1; z++) {
					if ((x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2) {
					   continue;
					}
					if ((x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2) {
						continue;
					}
					welt.blocks[[x, y, z]] = t;
				}
			}
			s -= d;  // decrement side lenth so hills taper off
		}
	}

	// place trees
	for (let i = 0; i < 5; i++) {
		var x = random.randint(-o, o);  // x position des Baumes
		var z = random.randint(-o, o);  // z position des Baumes
		var y = -1;                     // Basis des Baums
		while ((welt.blocks[[x,y,z]] || "AIR") != "AIR") {
			y += 1;
		}
		let imax = random.randint(3,4);
		for (let i = 0; i < imax; i++) {
			welt.blocks[[x, y, z]] = "BRAUN";
			y += 1;

			let a = x;
			let b = z;
			let c = y;
			let h = random.randint(2, 3);  // seite des Baums 
			let s = random.randint(4, 6);  // seite des baume
			let d = 1;
			for (y = c; y < c+h; y++) {
				for (x = a - s; x < a + s + 1; x++) {
					for (z = b - s; z < b + s + 1; z++) {
						if ((x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2) {
							continue;
						}
						if ((x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2) {
							continue;
						}
						welt.blocks[[x, y, z]] = "HELLGRUN";
					}
				}
				s -= d;  // decrement side lenth so hills taper off
			}
		}
	}

}

console.log("calling init");
init();
console.log("init finished");

function terrain (position) {
	var [x,y,z] = position;
	// lookup
	var block = welt.blocks[[x,y,z]];
	if (block != null) {
		return block;
	}
	// basic world stuff
	if ((Math.abs(x) <= n) && (Math.abs(z) <= n)) {
		// border
		if ((Math.abs(x) == n) || (Math.abs(z) == n)) {
			return ((-14 < y) && (y < 4)) ? "STONE" : "AIR";
		}
		// ground layers
		else {
			return ["AIR","AIR","GRUN","BRAUN","BRAUN","BRAUN","GRAU","GRAU","GRAU","GRAU","GRAU","GRAU","GRAU","STONE"][-y] || "AIR";
		}
	}
	return "AIR";
}
