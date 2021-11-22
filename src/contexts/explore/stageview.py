from math import inf
from pygame import Surface
from lib.sprite import Sprite
import lib.vector as vector
from config import WINDOW_HEIGHT, DEPTH_SIZE

class StageView:
  LAYERS = ["tiles", "decors", "elems", "vfx", "numbers", "ui"]

  def order(sprite):
    if type(sprite) is list:
      return inf
    _, sprite_y = sprite.pos
    try:
      depth = StageView.LAYERS.index(sprite.layer)
    except ValueError:
      depth = 0
    depth *= WINDOW_HEIGHT * DEPTH_SIZE
    y = (sprite_y + sprite.offset + 0.5) * DEPTH_SIZE
    return int(depth + y)

  def __init__(view, stage, camera, anims):
    view.stage = stage
    view.camera = camera
    view.anims = anims

  def update(view):
    if view.anims:
      view.anims[0] = [(a.update(), a)[-1] for a in view.anims[0] if not a.done]
    view.anims = [g for g in view.anims if g]

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

  def view_elems(view, elems):
    sprites = []

    for elem in elems:
      elem_sprites = Sprite.move_all(
        sprites=elem.view(anims=view.anims),
        offset=elem.pos,
      )
      elem_sprites[0].origin = Sprite.ORIGIN_CENTER
      sprites += elem_sprites

    return sprites

  def view(view):
    stage = view.stage
    sprites = []

    sprites += view.view_tiles(stage.tiles)
    sprites += view.view_elems(stage.elems)

    sprites.sort(key=StageView.order)
    sprites = Sprite.move_all(
      sprites=sprites,
      offset=vector.negate(view.camera.rect.topleft)
    )

    return sprites
