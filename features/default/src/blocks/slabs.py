from resources import *

@alias("STONESLAB")
class _SlabBlock(Block):
    def collides_with(self, area):
        """
        if a block is solid and his bounding box collides with <area>,
        this method is used to test if they actually collide
        """
        b1 = self.block_to_world_vector(Vector(-0.5,-0.5,-0.5))
        b2 = self.block_to_world_vector(Vector( 0.5,   0, 0.5))
        lower_bounds = map(min, b1, b2)
        upper_bounds = map(max, b1, b2)
        hitbox = Box(lower_bounds,upper_bounds)
        return area.collides_with(hitbox + self.position)
