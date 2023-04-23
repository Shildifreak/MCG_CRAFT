
function cached (det_f) {
    var cache = new Map();
    return function _f (position) {
        var cachekey = JSON.stringify(position);
        var value;
        if (cache.has(cachekey)) {
            value = cache.get(cachekey);
        } else {
            value = det_f(position);
            cache.set(cachekey, value);
        }
        return value;
    }
}

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

function noise32(seed=null) {
    if (seed === null) {
        seed = 0;
    }
    return function (position) {
        position.push(seed);
        var value = 0;
        for (var coordinate of position) {
            coordinate = 2*Math.abs(coordinate)+(coordinate<0);
            value = hash(value ^ coordinate);
        }
        return value;
    }
}

function noise(seed=null) {
    var _noise32 = noise32(seed);
    return function (position) {
        return _noise32(position) / (1<<32);
    }
}

function constant_weight (/*arguments*/) {
    return 1;
}

function linear_weight (dx, dz) {
    return Math.max(0,1-Math.abs(dx)) * Math.max(0,1-Math.abs(dz));
}

function polynomial_weight (dx, dz) {
    var dx = Math.max(0,1-Math.abs(dx));
    var dz = Math.max(0,1-Math.abs(dz));
    return (Math.pow(3*dx, 2) - Math.pow(2*dx, 3)) * (Math.pow(3*dz, 2) - Math.pow(2*dz,3));
}

function mod_map(f, options) {
    var l = options.length;
    return cached(function (position) {
        var h = f(position);
        return options[h%l];
    });
}

function count2d(f, d, k=1, w=constant_weight) {
    return function (position) {
        var [x, z] = position;
        var xk = x/k;
        var zk = z/k;
        var xi = Math.floor(xk);
        var zi = Math.floor(zk);
        var xr = xk - xi;
        var zr = zk - zi;
        
        var counter = new Map();
        for (var dx = -d; dx < d+2; dx++) {
            for (var dz = -d; dz < d+2; dz++) {
                var t = f([xi+dx, zi+dz]);
                var v = counter.get(t);
                if (v == undefined) {
                    v = 0;
                }
                v += w((dx-xr)/(d+1),(dz-zr)/(d+1));
                counter.set(t,v);
            }
        }
        return counter;
    }
}

function count3d(f, d, k=1, w=constant_weight) {
    return function (position) {
        var [x, y, z] = position;
        var xk = x/k;
        var yk = y/k;
        var zk = z/k;
        var xi = Math.floor(xk);
        var yi = Math.floor(yk);
        var zi = Math.floor(zk);
        var xr = xk - xi;
        var yr = yk - yi;
        var zr = zk - zi;
        
        var counter = new Map();
        for (var dx = -d; dx < d+2; dx++) {
            for (var dy = -d; dy < d+2; dy++) {
                for (var dz = -d; dz < d+2; dz++) {
                    t = f([xi+dx, yi+dy, zi+dz]);
                    var v = counter.get(t);
                    if (v == undefined) {
                        v = 0;
                    }
                    v += w((dx-xr)/(d+1), (dy-yr)/(d+1), (dz-zr)/(d+1));
                    counter.set(t,v);
                }
            }
        }
        return counter;
    }
}

function majority (f) {
    return cached(function (position) {
        var counter = f(position);
        var max_value = 0;
        var max_key = null;
        for (var [key, value] of counter.entries()) {
            if (value > max_value) {
                max_key = key;
                max_value = value;
            }
        }
        return max_key;
    });
}

function sum (f) {
    return cached(function (position) {
        var counter = f(position);
        var sum = 0;
        for (var [key, value] of counter.entries()) {
            sum += key * value;
        }
        return sum;
    });
}

function mul (f, k) {
	return function (position) {
		return k * f(position);
	}
}

function tunnel (f, t=2) {
    return cached(function (position) {
        var counter = f(position);
        return (counter.size>=t) && (! counter.has(0));
    });
}

function threshold(f, t) {
    return function (position) {
        return f(position) >= t;
    }
}

function apply_filter (f /*, implicit filter_factory_list*/) {
    for (var i = 1; i<arguments.length; i++) {
        var [filter_factory, ...args] = arguments[i];
        f = filter_factory(f, ...args);
    }
    return f;
}


var biome_terrain = apply_filter(noise32(seed),
    [mod_map, [0,1,2]],
    [count2d, 3],
    [majority],
    [count2d, 3],
    [majority],
    [count2d, 3],
    [majority],
    [count2d, 2, 8, polynomial_weight],
    [majority],
    [mod_map, ["MOUNTAIN","GRASSLAND","DESERT"]],
)

var tunnel_terrain = apply_filter(noise32(seed),
    [mod_map, [0,0,0,0,0,0,0,0,0,
               1,1,1,1,1,1,1,1,1,1,1,
               2,2,2,2,2,2,2,2,2,2,2,
               3,3,3,3,3,3,3,3,3,3]],
    [count2d, 3],
    [majority],
    [count2d, 3],
    [majority],
    [count2d, 3],
    [majority],
    [count2d, 1],
    [tunnel],
    [count2d, 1, 2, polynomial_weight],
    [majority],
    [threshold, 1],
    [mod_map, ["GRASS", "AIR"]],
)

var tunnel3d_terrain = apply_filter(noise32(seed),
    [mod_map, [0,0,0,0,0,0,0,0,0,
               1,1,1,1,1,1,1,1,1,1,1,
               2,2,2,2,2,2,2,2,2,2,2,
               3,3,3,3,3,3,3,3,3,3]],
    [count3d, 2,2],
    [majority],
    [count3d, 2],
    [majority],
    [count3d, 1],
    [tunnel, 3],
    //[count3d, 0, 2],
    //[majority],
    [mod_map, ["AIR", "STONE"]],
)

var mountain_terrain_height = apply_filter(noise32(seed),
	[mod_map, [-5, -5,
			   0, 0,
			   5, 5,
			   20]],
	[count2d, 1, 5, polynomial_weight],
	[sum],
	[mul, 0.2],
)

var grassland_terrain_height = apply_filter(noise32(seed),
	[mod_map, [-2, 0, 2, 3]],
	[count2d, 3, 1, linear_weight],
	[majority],
	[count2d, 3, 3, polynomial_weight],
	[sum],
	[mul, 0.03],
)

function terrain(position) {
	var [x,y,z] = position;
	var b = biome_terrain([x, z]);
	if (b == "MOUNTAIN") {
    	var h = mountain_terrain_height([x,z]);
		if (y <= h) {
			if (y < 15) {
				return "STONE";
			} else {
				return "SCHNEE";
			}
		}
	}
	if (b == "GRASSLAND") {
    	var h = Math.floor(grassland_terrain_height([x,z]));
		if (y < h) {
			return "DIRT"
		}
		if (y == h) {
			if (y < 0) {
				return "DIRT"
			} else {
				return "GRASS"
			}
		}
		if (y <= 0) {
			return "WATER"
		}
	}
	if (b == "DESERT") {
		if (y <= 0) {
			return "SAND"
		}
	}
	return "AIR";
	
        //return tunnel_terrain([x, z]);
	/*
    } else
    if ((position[0] == 0) && (position[1] == 0) && (position[2] == 0)) {
        return "DIAMANT";
    } else
    if (position[1] <= 0) {
        return tunnel3d_terrain(position);
    } else {
        return "AIR";
    }
	*/
};

function terrain_hint(binary_box, tag) {
    if (tag == "visible") {
        if (binary_box[1][1] == 0) {
            return true;
        }
        return true;
        //return false;
    }
    return true;
}

// spawnpoint
function generate_spawnpoint() {
    var [x, y, z] = [0, 0, 0];
    for (var i = 0; i < 100; i++) {
        let b = (terrain([0,y+1,0]) != "AIR")*4
              + (terrain([0,y  ,0]) != "AIR")*2
              + (terrain([0,y-1,0]) != "AIR")*1;
        if (b == 1) {
            break;
        }
        (b > 1) ? y++ : y--;
    }
    let dy = 1.6 - 0.5 + 0.1; // player eye level, block center to surface, margin
    return [x, y + dy, z];
}
var spawnpoint = generate_spawnpoint();
