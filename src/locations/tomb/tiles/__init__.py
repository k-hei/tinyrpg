import lib.vector as vector
from lib.sprite import Sprite
from lib.filters import replace_color

import assets
from colors.palette import WHITE, COLOR_TILE, COLOR_TILE_ALT
from config import TILE_SIZE

from dungeon.props.door import Door
from dungeon.props.secretdoor import SecretDoor

from locations.tomb.tiles.walltop import render_walltop
from locations.tomb.tiles.oasis import render_oasis
from locations.tileset import Tileset
from locations.default.tile import Tile
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

import debug


tileset_color = WHITE
tileset_backups = {}


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
        and (room := next((r for r in stage.rooms if cell in r.cells), None))
        and (elem := next((e for e in stage.elems
            if e.cell[0] == x
            and e.cell[1] <= y + 1
            and e.cell in room.cells
        ), None))):
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
        neighbors = {
            (x - 1, y - 1),
            (    x, y - 1),
            (x + 1, y - 1),
            (x - 1,     y),
            (x + 1,     y),
            (x - 1, y + 1),
            (    x, y + 1),
            (x + 1, y + 1),
        }
        return [
            stage.get_tile_at((x - 1, y)),
            stage.get_tile_at((x + 1, y)),
            stage.get_tile_at((x, y - 1)),
            stage.get_tile_at((x, y + 1)),
            *[n in visited_cells for n in neighbors]
        ]

    @classmethod
    def render(cls, stage, cell, visited_cells=None):
        x, y = cell
        tile_below = stage.get_tile_at((x, y + 1))
        tile_base = stage.get_tile_at((x, y + 2))
        is_elevated = False
        is_special_room = False

        if (Tile.is_of_type(tile_below, (Floor, Pit, Hallway, Oasis))
        and (visited_cells is None or (x, y + 1) in visited_cells)
        and not next((e for e in stage.get_elems_at((x, y + 1)) if isinstance(e, Door)), None)):
            if is_special_room:
                if x % (2 + y % 2) == 0 or SecretDoor.exists_at(stage, cell):
                    return assets.sprites["wall_battle_alt"]
                else:
                    return assets.sprites["wall_battle"]
            else:
                if x % (3 + y % 2) == 0 or SecretDoor.exists_at(stage, cell):
                    return assets.sprites["wall_alt"]
                else:
                    return assets.sprites["wall_bottom"]
        elif is_elevated and tile_below is Wall and not (tile_base is None or tile_base is Wall):
            return assets.sprites["wall_top"]
        else:
            return render_walltop(stage, cell, visited_cells)

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
    sprite = "stairs_down"

class Exit(DefaultExit):
    sprite = "stairs_up"

class Escape(DefaultEscape):
    sprite = "stairs_up"

class Oasis(DefaultOasis):
    @classmethod
    def render(cls, stage, cell, visited_cells):
        return render_oasis(stage, cell, visited_cells)

class OasisStairs(DefaultOasisStairs):
    @classmethod
    def render(cls, stage, cell, _):
        x, y = cell
        if stage.is_tile_at_of_type((x, y - 1), Floor):
            return assets.sprites["oasis_stairs_down"]
        else:
            return assets.sprites["oasis_stairs_up"]


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
        "O": Oasis,
        "I": OasisStairs,
    }

    Floor = Floor
    Wall = Wall
    Pit = Pit
    Hallway = Hallway
    Entrance = Entrance
    Exit = Exit
    Escape = Escape
    Oasis = Oasis
    OasisStairs = OasisStairs

    @classmethod
    def recolor_tiles(cls, new_color=COLOR_TILE):
        global tileset_color
        if tileset_color == new_color:
            return False

        TILE_SPRITE_IDS = [
            "tomb_floor",
            "wall_top",
            "wall_bottom",
            "wall_alt",
            "wall_battle",
            "wall_battle_alt",
            "wall_corner*",
            "wall_edge*",
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

        all_sprite_ids = []
        for tile_sprite_id in TILE_SPRITE_IDS:
            if tile_sprite_id.endswith("*"):
                tile_sprite_id = tile_sprite_id[:-1]
                all_sprite_ids += [s for s in assets.sprites if s.startswith(tile_sprite_id)]
            all_sprite_ids.append(tile_sprite_id)

        for tile_sprite_id in all_sprite_ids:
            assets.sprites[tile_sprite_id] = replace_color(assets.sprites[tile_sprite_id],
                old_color=tileset_color,
                new_color=new_color)

        debug.log(f"recolor tileset from {tileset_color} to {new_color}")
        tileset_color = new_color
        return True

    @staticmethod
    def find_stage_color(stage):
        return COLOR_TILE_ALT if stage.generator == "GenericFloor" else COLOR_TILE

    @classmethod
    def is_tile_at_solid(cls, tile):
        return cls.is_tile_at_wall(tile)

    @staticmethod
    def is_tile_at_of_type(tile, tile_type):
        return Tile.is_of_type(tile, tile_type)

    @classmethod
    def is_tile_at_wall(cls, tile):
        return cls.is_tile_at_of_type(tile, Wall)

    @classmethod
    def is_tile_at_hallway(cls, tile):
        return cls.is_tile_at_of_type(tile, Hallway)

    @classmethod
    def is_tile_at_pit(cls, tile):
        return cls.is_tile_at_of_type(tile, Pit)

    @classmethod
    def is_tile_at_oasis(cls, tile):
        return cls.is_tile_at_of_type(tile, Oasis)

    @classmethod
    def is_tile_at_port(cls, tile):
        return cls.is_tile_at_of_type(tile, (Entrance, Exit, Escape))

    @staticmethod
    def find_tile_state(tile, stage, cell, visited_cells):
        if not tile:
            return None

        return tile.find_state(stage, cell, visited_cells)

    @classmethod
    def render_tile(cls, tile, stage, cell, visited_cells):
        if not tile:
            return None

        stage_color = cls.find_stage_color(stage)
        cls.recolor_tiles(stage_color)

        return tile.render(stage, cell, visited_cells)
