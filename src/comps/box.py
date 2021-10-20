from pygame import Surface
from colors.palette import WHITE
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
    surface = Surface(box.size)
    surface.fill(WHITE)

    sprite_prefix = box and box.sprite_prefix
    tile_size = assets.sprites[f"{sprite_prefix}_c"].get_width()
    width, height = box.size

    cols = width // tile_size
    for col in range(cols):
      surface.blit(assets.sprites[f"{sprite_prefix}_n"], (col * tile_size, 0))
      surface.blit(assets.sprites[f"{sprite_prefix}_s"], (col * tile_size, height - tile_size))

    rows = height // tile_size
    for row in range(rows):
      surface.blit(assets.sprites[f"{sprite_prefix}_w"], (0, row * tile_size))
      surface.blit(assets.sprites[f"{sprite_prefix}_e"], (width - tile_size, row * tile_size))

    surface.blit(assets.sprites[f"{sprite_prefix}_nw"], (0, 0))
    surface.blit(assets.sprites[f"{sprite_prefix}_sw"], (0, height - tile_size))
    surface.blit(assets.sprites[f"{sprite_prefix}_ne"], (width - tile_size, 0))
    surface.blit(assets.sprites[f"{sprite_prefix}_se"], (width - tile_size, height - tile_size))
    return surface
