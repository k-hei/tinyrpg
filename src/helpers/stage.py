from dungeon.actors import DungeonActor
from config import TILE_SIZE


def find_tile(stage, tile):
    return next((c for c, t in stage.tiles.enumerate()
        if t == tile
        or t and isinstance(t, type) and isinstance(tile, type) and issubclass(t, tile)
    ), None)

def is_tile_walkable_to_actor(stage, cell, actor):
    return (cell in stage
        and not stage.is_tile_at_solid(cell, scale=TILE_SIZE)
        and (not stage.is_tile_at_pit(cell) or actor.floating))

def is_cell_walkable_to_actor(stage, cell, actor, ignore_actors=False):
    return (is_tile_walkable_to_actor(stage, cell, actor)
        and not stage.is_cell_occupied(cell, ignore_actors=ignore_actors))
