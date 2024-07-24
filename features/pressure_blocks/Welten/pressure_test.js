var spawnpoint = [0,5,0];

function terrain(position) {
    if (position[1] <= 0) {
        return "STONE"; // random.choice(["STONE","GRASS","DIRT"])
    } else {
        return "COMPRESSED_AIR";
    }
};

function terrain_hint(binary_box, tag) {
    if (tag == "visible") {
        if (binary_box[1][1] == 0) {
            return true;
        }
        return false;
    }
    return true;
}

