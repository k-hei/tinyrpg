import lib.vector as vector
from lib.sprite import Sprite
from lib.filters import replace_color

import assets
from colors.palette import WHITE, COLOR_TILE
from config import TILE_SIZE
from locations.tileset import Tileset
from locations.default.tileset import (
    black_square,
    Floor as DefaultFloor,
    Wall as DefaultWall,
    Pit as DefaultPit,
    Hallway as DefaultHallway,
    Entrance as DefaultEntrance,
    Exit as DefaultExit,
    Escape as DefaultEscape,
    Oasis as DefaultOasis,
    OasisStairs as DefaultOasisStairs,
)


def recolor_tiles():
    TILE_SPRITE_IDS = [
        "tomb_floor",
        "wall_top",
        "wall_bottom",
        "wall_alt",
        "wall_battle",
        "wall_battle_alt",
        "wall_corner",
        "wall_edge",
        "wall_link",
        "stairs_up",
        "stairs_down",
        "oasis_edge",
        "oasis_edge_top",
        "oasis_edge_bottom",
        "oasis_corner_top",
        "oasis_corner_bottom",
        "oasis_stairs_down",
        "oasis_stairs_up",
    ]
    for tile_sprite_id in TILE_SPRITE_IDS:
        assets.sprites[tile_sprite_id] = replace_color(assets.sprites[tile_sprite_id], WHITE, COLOR_TILE)

recolor_tiles()


class Floor(DefaultFloor):
    @staticmethod
    def find_state(stage, cell, *_):
        x, y = cell
        return [
            stage.get_tile_at(cell),
            stage.get_tile_at((x, y - 1)),
        ]

    @classmethod
    def render(cls, stage, cell, *_):
        x, y = cell
        if (stage.get_tile_at((x, y - 1)) is Pit
        and next((e for e in stage.elems if e.cell[1] < y), None)):
            return Sprite(
                image=assets.sprites["tomb_floor"],
                layer="elems",
                offset=-1,
            )
        else:
            return assets.sprites["tomb_floor"]

class Wall(DefaultWall):
    @staticmethod
    def find_state(stage, cell, visited_cells):
        x, y = cell
        return [
            stage.get_tile_at(cell),
            stage.get_tile_at((x - 1, y)),
            stage.get_tile_at((x + 1, y)),
            stage.get_tile_at((x, y - 1)),
            stage.get_tile_at((x, y + 1)),
            (x - 1, y - 1) in visited_cells,
            (    x, y - 1) in visited_cells,
            (x + 1, y - 1) in visited_cells,
            (x - 1,     y) in visited_cells,
            (x + 1,     y) in visited_cells,
            (x - 1, y + 1) in visited_cells,
            (    x, y + 1) in visited_cells,
            (x + 1, y + 1) in visited_cells,
        ]

    @classmethod
    def render(cls, stage, cell, visited_cells=None):
        return assets.sprites["wall_top"]
        # x, y = cell
        # tile_below = stage.get_tile_at((x, y + 1))
        # tile_base = stage.get_tile_at((x, y + 2))
        # is_elevated = False
        # is_special_room = False

        # if (
        #   Tile.is_of_type(tile_below, (Floor, Pit, DefaultHallway, Oasis))
        #   and (visited_cells is None or (x, y + 1) in visited_cells)
        #   and not next((e for e in stage.get_elems_at((x, y + 1)) if isinstance(e, Door)), None)
        # ):
        #   if is_special_room:
        #     if x % (2 + y % 2) == 0 or SecretDoor.exists_at(stage, cell):
        #       return assets.sprites["wall_battle_alt"]
        #     else:
        #       return assets.sprites["wall_battle"]
        #   else:
        #     if x % (3 + y % 2) == 0 or SecretDoor.exists_at(stage, cell):
        #       return assets.sprites["wall_alt"]
        #     else:
        #       return assets.sprites["wall_bottom"]
        # elif is_elevated and tile_below is Wall and not (tile_base is None or tile_base is Wall):
        #   return assets.sprites["wall_top"]
        # else:
        #   return render_walltop(stage, cell, visited_cells)

class Hallway(DefaultHallway):
    sprite = black_square

class Pit(DefaultPit):
    @staticmethod
    def find_state(stage, cell, visited_cells):
        x, y = cell
        return [
            stage.get_tile_at(cell),
            stage.get_tile_at((x, y - 1)),
            (x, y - 1) in visited_cells,
        ]

    @classmethod
    def render(cls, stage, cell, *_):
        return (assets.sprites["tomb_pit"]
            if stage.get_tile_at(vector.add(cell, (0, -1))) is not Pit
            else black_square)

class Entrance(DefaultEntrance):
    sprite = assets.sprites["stairs_up"]

class Exit(DefaultExit):
    sprite = assets.sprites["stairs_down"]

class Escape(DefaultEscape):
    sprite = assets.sprites["stairs_up"]


class TombTileset(Tileset):
    tile_size = TILE_SIZE
    mappings = {
        ".": Floor,
        "#": Wall,
        " ": Pit,
        ",": Hallway,
        "<": Entrance,
        ">": Exit,
        "E": Escape,
        # "O": Oasis,
        # "I": OasisStairs,
    }

    Floor = Floor
    Wall = Wall
    Pit = Pit
    Hallway = Hallway
    Entrance = Entrance
    Exit = Exit
    Escape = Escape

    @classmethod
    def is_tile_at_solid(cls, tile):
        return cls.is_tile_at_wall(tile)

    @staticmethod
    def is_tile_at_wall(tile):
        return (tile[0] is Wall
            if isinstance(tile, (list, tuple))
            else tile is Wall)

    @staticmethod
    def is_tile_at_pit(tile):
        return (tile[0] is Pit
            if isinstance(tile, (list, tuple))
            else tile is Pit)

    @staticmethod
    def find_tile_state(tile, stage, cell, visited_cells):
        if not tile:
            return None

        return tile.find_state(stage, cell, visited_cells)

    @staticmethod
    def render_tile(tile, stage, cell, visited_cells):
        if not tile:
            return None

        return tile.render(stage, cell, visited_cells)
