var spawnpoint = [0,5,0];

function terrain(position) {
    var [x,y,z] = position;
    if ((x == 10) && (y == 0) && (z == 0)) {
        return {"id":"INITPRINT", "info": "part of terrain"};
    }
    if (y <= 0) {
        return "STONE";
    }
    return "AIR";
};
