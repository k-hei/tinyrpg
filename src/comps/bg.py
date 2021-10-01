from math import ceil
from pygame import Surface
from assets import load as use_assets

class Bg:
  PERIOD = 90

  def render(size):
    width, height = size
    tile_image = use_assets().sprites["bg_tile"]
    tile_width = tile_image.get_width()
    tile_height = tile_image.get_height()
    tile_surface = Surface((width + tile_width, height + tile_height))
    for row in range(ceil(tile_surface.get_height() / tile_height)):
      for col in range(ceil(tile_surface.get_width() / tile_width)):
        x = col * tile_width
        y = row * tile_height
        tile_surface.blit(tile_image, (x, y))
    return tile_surface

  def __init__(bg, size):
    bg.size = size
    bg.surface = None
    bg.time = 0

  def init(bg):
    bg.surface = Bg.render(bg.size)

  def update(bg):
    bg.time += 1

  def draw(bg, surface):
    surface.blit(bg.surface, (0, 0))
    tile_size = use_assets().sprites["bg_tile"].get_width()
    t = bg.time % bg.PERIOD / bg.PERIOD
    x = -t * tile_size
    surface.blit(bg.surface, (x, x))
    bg.update()
