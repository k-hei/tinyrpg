from lib.grid import Grid
from lib.bounds import find_bounds
import lib.vector as vector
from lib.cell import neighborhood

from contexts.explore.stage import Stage
from contexts.explore.roomdata import RoomData
from contexts.explore.tile_matrix import TileMatrix
from dungeon.room import Blob as Room
from dungeon.decoder import decode_elem
from dungeon.props.door import Door
from dungeon.actors import DungeonActor
import locations.default.tileset as default_tileset
from locations.tileset import Tileset
from helpers.stage import find_tile

from config import TILE_SIZE
import debug


def manifest_rooms(rooms, tileset, dry=False, seed=None):
    stage_cells = []
    for room in rooms:
        stage_cells += room.cells

    stage_blob = Room(stage_cells, origin=(1, 2))
    stage_offset = vector.subtract(stage_blob.origin, find_bounds(stage_cells).topleft)

    stage_tiles = Grid(size=vector.add(stage_blob.rect.size, (2, 3)))
    stage_tiles.fill(tileset.Wall)

    stage = Stage(
        tiles=TileMatrix(layers=[stage_tiles]),
        tileset=tileset,
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

def validate_room_data(room_data):
    if not isinstance(room_data, RoomData):
        raise TypeError(f"Failed to manifest room: Invalid room data '{room_data}'")

    if not Tileset.is_tileset(room_data.bg):
        raise TypeError(f"Failed to manifest room: Invalid tileset '{room_data.bg}'")

def manifest_stage_from_overworld_room(room_data):
    validate_room_data(room_data)
    stage = Stage(
        name=room_data.name,
        tileset=room_data.bg,
        tiles=room_data.tiles,
        rooms=[Room(data=room_data)],
    )
    stage.collision_whitelist = room_data.collision_whitelist
    return stage

def manifest_stage_from_dungeon_room(room_data):
    validate_room_data(room_data)
    room_tileset = room_data.bg

    stage_tiles = Grid(size=vector.add(room_data.size, (2, 3)))
    stage_tiles.fill(room_tileset.Wall)

    room = Room(data=room_data, origin=(1, 2))
    room_width, room_height = room_data.size
    for row in range(room_height):
        for col in range(room_width):
            room_cell = (col, row)
            stage_cell = vector.add(room_cell, room.origin)
            stage_tiles[stage_cell] = room_data.tiles[room_cell][0]

    return Stage(
        name=room_data.name,
        tileset=room_data.bg,
        tiles=TileMatrix(layers=[stage_tiles]),
        rooms=[room],
    )

def manifest_room(room_data, port_id=None):
    validate_room_data(room_data)

    room_tileset = room_data.bg
    manifestor = (manifest_stage_from_overworld_room
        if room_tileset.is_overworld_room
        else manifest_stage_from_dungeon_room)

    stage = manifestor(room_data)
    stage.generator = room_data
    room = stage.rooms[0]

    if port_id:
        port = room_data.ports[port_id]
        stage.entrance = vector.subtract(
            port.cell,
            vector.scale(port.direction, 2)
        )

    # TODO: fix hardcoded edge types
    if stage.entrance is None:
        stage.entrance = (
            find_tile(stage, default_tileset.Escape)
            or find_tile(stage, default_tileset.Entrance)
            or find_tile(stage, default_tileset.Exit)
        )

    if stage.entrance is None:
        stage.entrance = vector.add(room_data.edges[-1], room.origin)

    if (not room_tileset.is_overworld_room
    and stage.is_tile_at_of_type(stage.entrance, room_tileset.Wall)):
        stage.set_tile_at(stage.entrance, room_tileset.Hallway)
        stage.spawn_elem_at(stage.entrance, Door(opened=True))

    spawn_elems(stage,
        elem_data=room_data.elems,
        tileset=room_tileset,
        offset=room.origin)

    enemies = [e for e in stage.elems
        if isinstance(e, DungeonActor)
        and e.faction == "enemy"]

    room.on_place(stage)

    if stage.is_overworld_room:
        enemy_territories = [find_territory(stage, e.cell) for e in enemies]
        enemy_territories = merge_territories(stage, enemy_territories)
        stage.rooms = [Room(t) for t in enemy_territories] + stage.rooms
        for enemy in enemies:
            enemy.ai_spawn = enemy.cell
            enemy.ai_territory = next((r for r in stage.rooms if enemy.cell in r.cells), None)

    return stage

def find_territory(stage, cell):
    return [c for c in neighborhood(
        cell=cell,
        radius=3,
        diagonals=True,
        inclusive=True,
        predicate=lambda c: (
            stage.is_cell_empty(c, scale=TILE_SIZE)
        )
    )]

def merge_territories(stage, territories):
    merged_territories = territories.copy()

    merged = True
    while merged:
        merged = False
        for i, territory in enumerate(merged_territories):
            territory_set = set(territory)
            for other_territory in merged_territories[i+1:]:
                other_territory_set = set(other_territory)
                if territory_set & other_territory_set:
                    merged_territories[i] = list(territory_set | other_territory_set)
                    merged_territories.remove(other_territory)
                    merged = True
                    break
            if merged:
                break

    return merged_territories

def spawn_elems(stage, elem_data, offset=(0, 0), tileset=None):
    for elem_cell, elem_name, *elem_props in elem_data:
        elem_props = elem_props[0] if elem_props else {}
        elem = decode_elem(elem_cell, elem_name, elem_props, tileset)
        if not elem:
            debug.log("Failed to decode elem", elem_name)
            continue

        stage.spawn_elem_at(vector.add(offset, elem_cell), elem)
