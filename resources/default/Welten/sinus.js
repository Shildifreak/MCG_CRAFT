var spawnpoint = [0,20,0];

function terrain(position) {
	var [x,y,z] = position;
	let r = Math.sqrt(x*x+z*z);
	let d1 = 5 * Math.sqrt(r);
	let d2 = r + 2*Math.PI;
	let h = 100*Math.cos(d1)/(d2);

	if (y < -20) {
		return "AIR";
	}
	if (y == -20) {
		return "BEDROCK";
	}
	if (y < h-5) {
		return "GOLD";
	}
	if (y < h+1) {
		return "SAND";
	}
	if (y < 1) {
		return "GLAS";
	}
	
	return "AIR";
};
