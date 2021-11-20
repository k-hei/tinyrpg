from pygame import Surface
from lib.sprite import Sprite
import lib.vector as vector

class StageView:
  def __init__(view, stage=None):
    view.stage = stage

  def view_tiles(view, tiles):
    sprites = []

    for cell, tile in tiles.enumerate():
      tile_sprite = tile.sprite

      if callable(tile_sprite):
        tile_sprite = tile_sprite(view.stage, cell)

      if isinstance(tile_sprite, Surface):
        tile_sprite = Sprite(
          image=tile_sprite,
          pos=vector.scale(cell, view.stage.tile_size),
        )

      if tile_sprite:
        sprites.append(tile_sprite)

    return sprites

  def view(view):
    stage = view.stage
    sprites = []
    sprites += view.view_tiles(stage.tiles)
    return sprites
