import pygame.image
from os import path
from PIL import Image
from locations.tileset import Tileset
from untiled.tileset import find_tile_pos
from untiled.transform import extract_transform_mask, transform_image
from config import ASSETS_PATH, LOCATIONS_PATH


TILE_SIZE = 16
_solid_ids = [210, 211, 230, 231, 193, 213, 233, 215, 234, 235]
_tile_cache = {}

tileset_image = Image.open(path.join(ASSETS_PATH, "desert-tiles.png"))

class DesertTileset(Tileset):
    tile_size = TILE_SIZE
    elems_path = path.join(LOCATIONS_PATH, "desert", "elems.json")
    is_overworld = True

    @staticmethod
    def is_tile_at_solid(tile):
        tile_id, _ = extract_transform_mask(tile)
        return tile_id in _solid_ids

    @staticmethod
    def render_tile(tile, stage=None, cell=None, visited_cells=None):
        if tile == -1:
            return None

        if tile in _tile_cache:
            return _tile_cache[tile]

        tile_id, tile_mask = extract_transform_mask(tile)

        tile_x, tile_y = find_tile_pos(
            tile_id=tile_id,
            tile_size=TILE_SIZE,
            tileset_cols=tileset_image.width // TILE_SIZE
        )
        tile_image = tileset_image.crop((
            tile_x, tile_y,
            tile_x + TILE_SIZE, tile_y + TILE_SIZE
        ))
        tile_image = transform_image(image=tile_image, mask=tile_mask)

        tile_surface = pygame.image.fromstring(
            tile_image.tobytes(),
            tile_image.size,
            tile_image.mode
        )

        _tile_cache[tile] = tile_surface
        return tile_surface
