from lib.grid import Grid
from lib.bounds import find_bounds
import lib.vector as vector

from contexts.explore.stage import Stage
from contexts.explore.roomdata import RoomData
from dungeon.room import Blob as Room
from dungeon.decoder import decode_elem
import locations.tomb.tiles as tileset
from locations.tileset import Tileset
from helpers.stage import find_tile

def manifest_rooms(rooms, dry=False, seed=None):
    stage_cells = []
    for room in rooms:
        stage_cells += room.cells

    stage_blob = Room(stage_cells, origin=(1, 2))
    stage_offset = vector.subtract(stage_blob.origin, find_bounds(stage_cells).topleft)

    stage_tiles = Grid(size=vector.add(stage_blob.rect.size, (2, 3)))
    stage_tiles.fill(tileset.Wall)

    stage = Stage(
        tiles=stage_tiles,
        rooms=rooms,
        bg="tomb"
    )
    stage.seed = seed

    for room in rooms:
        for cell in room.cells:
            if room.data and room.data.tiles:
                tile = room.get_tile_at(vector.subtract(cell, room.origin))
            else:
                tile = tileset.Floor
            stage.set_tile_at(vector.add(cell, stage_offset), tile)

        if dry:
            continue

        room.origin = vector.add(room.origin, stage_offset)
        if room.data:
            spawn_elems(stage, elem_data=room.data.elems, offset=room.origin)

    return stage, stage_offset

def manifest_room(room):
    room_data = RoomData(**room)
    room_tileset = (room_data.bg
        if issubclass(room_data.bg, Tileset)
        else None)

    stage_rooms = [Room(cells) for cells in room_data.rooms] + [Room(data=room_data)]
    stage = Stage(
        tileset=room_data.bg,
        tiles=room_data.tiles,
        rooms=stage_rooms,
    )

    # TODO: fix hardcoded edge types
    if stage.entrance is None:
        stage.entrance = (
            find_tile(stage, tileset.Escape)
            or find_tile(stage, tileset.Entrance)
            or find_tile(stage, tileset.Exit)
        )

    if stage.entrance is None:
        stage.entrance = tuple(room_data.edges[-1])

    spawn_elems(stage, elem_data=room_data.elems, tileset=room_tileset)
    return stage

def spawn_elems(stage, elem_data, offset=(0, 0), tileset=None):
    for elem_cell, elem_name, *elem_props in elem_data:
        elem_props = elem_props[0] if elem_props else {}
        elem = decode_elem(elem_cell, elem_name, elem_props, tileset)
        stage.spawn_elem_at(vector.add(offset, elem_cell), elem)
