function terrain(position) {
    if (position[1] <= -200) {
        return "VOID";
    } else {
        return "AIR";
    }
};
