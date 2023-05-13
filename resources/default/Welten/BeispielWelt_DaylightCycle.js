var spawnpoint = [0, 5, 0]

function terrain(position) {
	var [x,y,z] = position;
	if (y < 0) {
		return "STONE";
	} else {
		return "AIR";
	}
}

function sky(position, time) {
	x = time/10;
	h = Math.max(-0.5, Math.min(0.5, 1.5*Math.sin(x))) + 0.5;
	return [0.5*h,0.69*h,1*h,1];
}
