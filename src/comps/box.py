from pygame import Surface, SRCALPHA
from colors.palette import BLACK, WHITE
from lib.filters import shadow_lite as shadow
import assets

class Box:
  TILE_SIZE = 8

  def __init__(box, sprite_prefix, size):
    box.sprite_prefix = sprite_prefix
    box.size = size

  @property
  def width(box):
    return box.size[0]

  @property
  def height(box):
    return box.size[1]

  def render(box):
    surface = Surface(box.size, flags=SRCALPHA)

    sprite_prefix = box and box.sprite_prefix
    tile_size = assets.sprites[f"{sprite_prefix}_c"].get_width()
    width, height = box.size

    rows = height // tile_size
    cols = width // tile_size
    for row in range(1, rows):
      for col in range(1, cols):
        surface.blit(assets.sprites[f"{sprite_prefix}_c"], (col * tile_size, row * tile_size))

    for col in range(1, cols):
      surface.blit(assets.sprites[f"{sprite_prefix}_n"], (col * tile_size, 0))
      surface.blit(assets.sprites[f"{sprite_prefix}_s"], (col * tile_size, height - tile_size))

    for row in range(1, rows):
      surface.blit(assets.sprites[f"{sprite_prefix}_w"], (0, row * tile_size))
      surface.blit(assets.sprites[f"{sprite_prefix}_e"], (width - tile_size, row * tile_size))

    surface.blit(assets.sprites[f"{sprite_prefix}_nw"], (0, 0))
    surface.blit(assets.sprites[f"{sprite_prefix}_sw"], (0, height - tile_size))
    surface.blit(assets.sprites[f"{sprite_prefix}_ne"], (width - tile_size, 0))
    surface.blit(assets.sprites[f"{sprite_prefix}_se"], (width - tile_size, height - tile_size))
    return surface
