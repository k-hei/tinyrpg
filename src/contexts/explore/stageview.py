from math import inf, ceil
from pygame import Surface, Rect, SRCALPHA
from lib.sprite import Sprite
from lib.animstep import step_anims
import lib.vector as vector
from lib.filters import darken_image
from contexts.dungeon.camera import Camera
from config import WINDOW_SIZE, WINDOW_HEIGHT, DEPTH_SIZE

def find_tile_state(stage, cell, visited_cells):
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

def render_tile(stage, cell):
  tile = stage.get_tile_at(cell)
  if tile is None:
    return None

  tile_image = tile.sprite
  if callable(tile_image):
    tile_image = tile_image(stage, cell)

  return tile_image

def snap_vector(vector, tile_size):
  return tuple(map(lambda x: x // tile_size, vector))

def snap_rect(rect, tile_size):
  return Rect(
    rect.left // tile_size - 1,
    rect.top // tile_size - 1,
    ceil(rect.width / tile_size) + 2,
    ceil(rect.height / tile_size) + 3
  )

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

  def __init__(view, stage, camera):
    view.stage = stage
    view.camera = camera
    view.anims = []
    view.vfx = []
    view.cache_camera_cell = None
    view.cache_visible_cells = []
    view.tile_surface = None
    view.tile_offset = (0, 0)
    view.tile_cache = {}

  def update(view):
    if view.anims:
      view.anims[0] = [(a.update(), a)[-1] for a in view.anims[0] if not a.done]
    view.anims = [g for g in view.anims if g]
    view.vfx = step_anims(view.vfx)

  def redraw_tile(view, stage, cell, visited_cells):
    tile = stage.get_tile_at(cell)
    if not tile:
      return False

    tile_name = tile.__name__
    tile_image = None

    tile_state = find_tile_state(stage, cell, visited_cells)
    cached_state, cached_image, _ = view.tile_cache[cell] if cell in view.tile_cache else (None, None, None)

    if cached_state and cached_state != tile_state:
      del view.tile_cache[cell]
      cached_state, cached_image = None, None

    if cached_image:
      tile_image = cached_image
    elif tile_name in view.tile_cache:
      tile_image = view.tile_cache[tile_name]
    else:
      tile_image = render_tile(stage, cell)

    if not tile_image:
      return False

    if cell not in view.tile_cache:
      view.tile_cache[cell] = (tile_state, tile_image, darken_image(tile_image))

    if tile_image:
      view.tile_surface.blit(
        tile_image,
        vector.scale(
          vector.subtract(cell, view.tile_offset),
          view.stage.tile_size
        )
      )

    return True

  def redraw_tiles(view, hero, visited_cells):
    TILE_SIZE = view.stage.tile_size

    total_rect = view.camera.rect.union(Camera(
      size=WINDOW_SIZE,
      pos=vector.scale(view.cache_camera_cell, TILE_SIZE),
    ).rect) if view.cache_camera_cell else view.camera.rect
    tile_rect = snap_rect(total_rect, TILE_SIZE)

    surface_size = vector.scale(tile_rect.size, TILE_SIZE)
    if view.tile_surface is None or surface_size != view.tile_surface.get_size():
      view.tile_surface = Surface(size=surface_size, flags=SRCALPHA)
    else:
      view.tile_surface.fill((0, 0, 0, 0))
    view.tile_offset = tile_rect.topleft

    for row in range(tile_rect.top, tile_rect.bottom + 1):
      for col in range(tile_rect.left, tile_rect.right + 1):
        cell = (col, row)
        if cell in hero.visible_cells:
          view.redraw_tile(view.stage, cell, visited_cells)
        elif cell in view.tile_cache:
          _, _, cached_image = view.tile_cache[cell]
          view.tile_surface.blit(
            cached_image,
            vector.scale(
              vector.subtract(cell, view.tile_offset),
              TILE_SIZE
            )
          )

    view.cache_camera_cell = snap_vector(view.camera.pos, TILE_SIZE)
    view.cache_visible_cells = hero.visible_cells.copy()

  def view_tiles(view, hero, visited_cells):
    if (view.tile_surface is None
    or view.cache_camera_cell != snap_vector(view.camera.pos, view.stage.tile_size)
    or view.cache_visible_cells != hero.visible_cells):
      view.redraw_tiles(hero, visited_cells)
    return [Sprite(
      image=view.tile_surface,
      pos=vector.add(
        vector.negate(view.camera.rect.topleft),
        vector.scale(view.tile_offset, view.stage.tile_size)
      )
    )]

  def view_elem(view, elem):
    elem_sprites = Sprite.move_all(
      sprites=elem.view(anims=view.anims),
      offset=elem.pos,
    )
    # if next((a for g in view.anims for a in g if a.target is elem), None):
      # print([(a.time, a.cell) for g in view.anims for a in g])
    if not elem_sprites:
      return []
    elem_sprites[0].origin = Sprite.ORIGIN_CENTER
    return elem_sprites

  def view_elems(view, elems):
    return [s for e in elems for s in view.view_elem(e)]

  def view_vfx(view, vfx):
    return [s for v in vfx for s in v.view()]

  def view(view, hero, visited_cells):
    sprites = []

    stage = view.stage
    sprites += view.view_elems(stage.elems)
    sprites += view.view_vfx(view.vfx)

    sprites = Sprite.move_all(
      sprites=sprites,
      offset=vector.negate(view.camera.rect.topleft)
    )

    sprites += view.view_tiles(hero, visited_cells)
    sprites.sort(key=StageView.order)
    return sprites
