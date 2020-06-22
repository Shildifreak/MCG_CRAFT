var spawnpoint = [0,0,0];

function mod(x,n) {
	return ((x%n)+n)%n;
}

function terrain(position) {
	var [x,y,z] = position;
	if (y <= -10) {
		return "STONE";
	} else if ((x&1) || (y&1) || (z&1)) {
		return "AIR";
	} else if (x == 0 && z == 0) {
		var b = (y < 0) ? "t" : "b";
		return {id:"TESTBLOCK", state:"", rotation:mod(Math.abs(y)/2,4), base:b};
	} else if (y == 0 && z == 0) {
		var b = (x < 0) ? "e" : "w";
		return {id:"TESTBLOCK", state:"", rotation:mod(Math.abs(x)/2,4), base:b};
	} else if (x == 0 && y == 0) {
		var b = (z < 0) ? "s" : "n";
		return {id:"TESTBLOCK", state:"", rotation:mod(Math.abs(z)/2,4), base:b};
	} else {
		return "AIR";
	}
}
