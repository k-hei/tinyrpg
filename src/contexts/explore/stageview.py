from math import inf, ceil
from pygame import draw, Surface, Rect, SRCALPHA
from lib.sprite import Sprite
from lib.animstep import step_anims
import lib.vector as vector
from lib.filters import darken_image
from anims.shake import ShakeAnim
from contexts.dungeon.camera import Camera, CameraConstraints
from dungeon.actors import DungeonActor
from dungeon.props.door import Door
from dungeon.props.secretdoor import SecretDoor
from config import WINDOW_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT, DEPTH_SIZE, TILE_SIZE
from resolve.tileset import resolve_tileset
import debug

import assets


def find_tile_hash(stage, cell, visited_cells, cache=None):
  """
  Gets the hash for the tile at the cell on the given stage.
  A tile hash is compared against a previous hash to determine whether or not the tile needs to be
  re-rendered. If a tile hash may differ between renders, then the tile is considered "dynamic", and
  "static" otherwise. Dynamic tiles may change appearance based on surrounding tiles, while static
  do not change appearance and can thus have their image stacks cached on initial render to avoid
  a significant amount of computational overhead.
  """
  if cache and cell in cache:
    return cache[cell]

  tileset = stage.tileset
  tiles = stage.get_tiles_at(cell)
  tile_hash = tuple([tileset.find_tile_state(t, stage, cell, visited_cells) for t in tiles])

  if cache:
    cache[cell] = tile_hash

  return tile_hash

def flatten_tile_image_stack(tile_images) -> Surface:
  """
  Flattens a tile image stack into a single surface.
  A tile image stack may contain Surface or Sprite instances.
  """
  tile_surface = None

  for image in tile_images:
    if isinstance(image, Sprite):
      image = image.image

    if not image:
      continue

    tile_surface = tile_surface or Surface(image.get_size(), flags=SRCALPHA)
    tile_surface.blit(image, (0, 0))

  return tile_surface

def convert_surface_to_sprite(surface):
  sprite_surface = Surface(size=surface.get_size(), flags=SRCALPHA)
  sprite_surface.blit(surface, (0, 0))
  return Sprite(
    image=sprite_surface,
    pos=(0, surface.get_height()),
    origin=Sprite.ORIGIN_BOTTOM,
    layer="elems",
  )

def render_tile(stage, cell, visited_cells=[]):
  tileset = stage.tileset
  tiles = stage.get_tiles_at(cell)
  tile_images = [tileset.render_tile(tile, stage, cell, visited_cells) for tile in tiles]
  tile_images = [convert_surface_to_sprite(image) if i and image else image
    for i, image in enumerate(tile_images)]
  return [image for image in tile_images if image]

def snap_vector(vector, tile_size):
  return tuple(map(lambda x: x // tile_size, vector))

def snap_rect(rect, tile_size):
  return Rect(
    rect.left // tile_size - 1,
    rect.top // tile_size - 1,
    ceil(rect.width / tile_size),
    ceil(rect.height / tile_size)
  )

class StageView:
  LAYERS = ["tiles", "decors", "elems", "vfx", "numbers", "ui"]

  @staticmethod
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

  def __init__(view, stage):
    view.stage = stage
    view.camera = Camera(WINDOW_SIZE, constraints=CameraConstraints(
      right=stage.width * stage.tile_size,
      bottom=stage.height * stage.tile_size,
    ) if stage.is_overworld else None)
    view.anim = None
    view.anims = []
    view.vfx = []
    view.darkened = False
    view.transitioning = False
    view.tile_layers = []
    view.tile_offset = (0, 0)
    view.tile_sprites = {}

  @property
  def stage(view):
    return view._stage

  @stage.setter
  def stage(view, stage):
    view._stage = stage
    view.reset_cache()

  def reset_cache(view):
    view.cache_camera_cell = None
    view.cache_tile_rect = None
    view.cache_visible_cells = []
    view.cache_visited_cells = []
    view.cache_elems = {}
    view.tile_cache = {}
    view.tile_sprites = {}
    view.tile_layers = []

  def update(view):
    if view.anims:
      view.anims[0] = [(a.update(), a)[-1] for a in view.anims[0] if not a.done]
    view.anims = [g for g in view.anims if g]

    if view.anim:
      if view.anim.done:
        view.anim = None
      else:
        view.anim.update()

    view.vfx = [(
      view.vfx.extend(f.update() or []),
      f
    )[-1] for f in view.vfx if not f.done]

  def shake(view, duration=15, vertical=False):
    view.anim = ShakeAnim(
      duration=duration,
      target=vertical,
      magnitude=2
    )

  def unshake(view):
    view.anim = None

  def darken(view):
    view.darkened = True
    view.cache_elems = {}

  def undarken(view):
    view.darkened = False

  def render_cell(view, stage, cell, visited_cells, use_cache=False, tile_hash_cache=None):
    tiles = stage.get_tile_at(cell)
    if not tiles:
      return None

    # get tile state (state of this cell and rendering-relevant neighbors)
    tile_hash = (None
      if stage.is_overworld
      else find_tile_hash(stage, cell, visited_cells, cache=tile_hash_cache))

    # read cached tile data
    cached_state, cached_images, cached_image = (
      view.tile_cache[cell]
        if cell in view.tile_cache
        else (None, None, None)
    )

    # clear cache for this cell if tile state has changed
    if cached_state and cached_state != tile_hash:
      del view.tile_cache[cell]
      if cell in view.tile_sprites:
        del view.tile_sprites[cell]
      cached_state, cached_images, cached_image = None, None, None

    tile_images = cached_images or render_tile(stage, cell, visited_cells)
    tile_sprites = [t for t in tile_images if isinstance(t, Sprite)]

    if tile_sprites and cell not in view.tile_sprites:
      for sprite in tile_sprites:
        sprite.move(vector.scale(cell, stage.tile_size))
      view.tile_sprites[cell] = tile_sprites

    if not cached_image and not stage.is_overworld:
      cached_image = flatten_tile_image_stack(tile_images)
      cached_image = cached_image and darken_image(cached_image)

    view.tile_cache[cell] = (tile_hash, tile_images, cached_image)

    if use_cache:
      # use darker version of tile for explicit cache usage (visited tile FOV)
      return [cached_image]

    return tile_images

  def redraw_tiles(view, hero, visited_cells, force=False):
    TILE_SIZE = view.stage.tile_size

    camera_rect = Rect(
      view.camera.rect.topleft,
      vector.add(WINDOW_SIZE, (TILE_SIZE * 2, TILE_SIZE * 2)),
    )

    tile_rect = snap_rect(camera_rect, TILE_SIZE)
    if (not force
    and tile_rect == view.cache_tile_rect
    and view.cache_visible_cells
    and view.cache_visited_cells):
      # camera rect is unchanged; no need to redraw
      return

    camera_cell_delta = (vector.subtract(tile_rect.topleft, view.cache_tile_rect.topleft)
      if view.cache_tile_rect
      else (0, 0))

    surface_size = vector.scale(tile_rect.size, TILE_SIZE)
    tile_layers = [Surface(size=surface_size, flags=SRCALPHA)
      for _ in range(view.stage.num_tile_layers)]

    if not view.tile_layers or surface_size != view.tile_layers[0].get_size():
      view.tile_layers = tile_layers
      view.cache_tile_rect = None
    else:
      cached_offset = vector.scale(vector.negate(camera_cell_delta), TILE_SIZE)
      for i, layer in enumerate(tile_layers):
        cached_layer = view.tile_layers[i]
        layer.blit(cached_layer, cached_offset)
      view.tile_layers = tile_layers

    view.tile_offset = tile_rect.topleft
    visible_cells = hero.visible_cells if hero else view.cache_visible_cells
    if not visible_cells:
      return

    if view.stage.is_overworld:
      viewable_cells = [(col, row)
        for row in range(tile_rect.top, tile_rect.bottom + 1)
          for col in range(tile_rect.left, tile_rect.right + 1)]
    else:
      viewable_cells = [c
        for c in visible_cells + visited_cells
          if tile_rect.collidepoint(c)]
      visible_cells = set(visible_cells)
      visited_cells = set(visited_cells)

    tile_hash_cache = {}

    for cell in viewable_cells:
      is_cell_visible = view.stage.is_overworld or cell in visible_cells

      has_cell_tile_state_changed = (not view.stage.is_overworld
        and is_cell_visible
        and cell in view.tile_cache
        and find_tile_hash(view.stage, cell, visited_cells, cache=tile_hash_cache) != view.tile_cache[cell][0])

      has_cell_visible_state_changed = (not view.stage.is_overworld
        and (is_cell_visible != (cell in view.cache_visible_cells)
          or (cell in visited_cells) != (cell in view.cache_visited_cells)))

      has_cell_been_rendered = view.cache_tile_rect and view.cache_tile_rect.collidepoint(cell)
      if (has_cell_been_rendered
      and not has_cell_tile_state_changed
      and not has_cell_visible_state_changed):
        # ignore previously drawn tiles if state is unchanged
        continue

      try:
        use_cache = view.darkened or (not view.stage.is_overworld and cell not in visible_cells)
        tile_images = view.render_cell(view.stage, cell, visited_cells, use_cache, tile_hash_cache=tile_hash_cache)
        if not tile_images:
          continue

        tile_pos = vector.scale(
          vector.subtract(cell, view.tile_offset),
          TILE_SIZE
        )

        if len(tile_images) == 1:
          tile_layer = view.tile_layers[0]
          tile_image = tile_images[0]
          if tile_image and not isinstance(tile_image, Sprite):
            tile_layer.blit(tile_image, tile_pos)
          continue

        # blit tile image stack onto associated layers
        # view.draw_tile_image_stack(tile_images, cell=vector.subtract(cell, view.tile_offset))
        for tile_layer, tile_image in zip(view.tile_layers, tile_images):
          if not tile_image or isinstance(tile_image, Sprite):
            # tile sprites get flattened for dim images, so no need to register a special case
            continue

          tile_layer.blit(tile_image, tile_pos)

      except Exception as e:
        debug.log(f"Failed to render tile {view.stage.get_tile_at(cell).__name__}")
        raise e

    view.cache_camera_cell = snap_vector(view.camera.pos, TILE_SIZE)
    view.cache_tile_rect = tile_rect
    view.cache_visible_cells = hero.visible_cells.copy()
    view.cache_visited_cells = visited_cells.copy()

  def view_tiles(view, hero, visited_cells):
    if (not view.tile_layers
    or view.cache_camera_cell != snap_vector(view.camera.pos, view.stage.tile_size)
    or hero and view.cache_visible_cells != hero.visible_cells
    or view.cache_visited_cells != visited_cells):
      view.redraw_tiles(hero, visited_cells)

    return [
      *view.view_tile_layers(),
      *view.view_tile_sprites(visited_cells)
    ]

  def view_tile_sprites(view, visited_cells):
    tile_sprites = []
    camera_rect = view.camera.rect
    for cell, sprites in view.tile_sprites.items():
      for sprite in sprites:
        if not camera_rect.colliderect(sprite.rect):
          continue

        if (view.stage.is_overworld
        or not view.darkened and cell in view.cache_visible_cells):
          tile_sprites.append(sprite.copy())
          continue

        if view.darkened or cell in visited_cells:
          tile_sprites.append(Sprite(
            image=view.tile_cache[cell][2],
            layer="tiles"
          ))

    for sprite in tile_sprites:
      sprite.move(vector.negate(view.camera.rect.topleft))

    return tile_sprites

  def view_tile_layers(view):
    return [Sprite(
      image=layer,
      pos=vector.subtract(
        vector.scale(view.tile_offset, view.stage.tile_size),
        view.camera.rect.topleft,
      ),
    ) for layer in view.tile_layers]

  def view_elem(view, elem, visited_cells=[]):
    if type(elem) is SecretDoor and elem.hidden:
      tileset = resolve_tileset(view.stage.bg)
      return [Sprite(
        image=tileset.Wall.render(view.stage, elem.cell, visited_cells),
        pos=tuple([x * view.stage.tile_size for x in elem.cell]),
        layer="tiles"
      )]

    elem_view = elem.view(anims=view.anims)
    if not elem_view:
      return []

    elem_sprites = Sprite.move_all(
      sprites=elem_view,
      offset=elem.pos,
    )

    if not elem_sprites:
      return []

    for elem_sprite in elem_sprites:
      if view.darkened and not isinstance(elem, DungeonActor):
        if elem not in view.cache_elems:
          view.cache_elems[elem] = darken_image(elem_sprite.image)
        elem_sprite.image = view.cache_elems[elem]

    elem_sprites[0].origin = elem_sprites[0].origin or Sprite.ORIGIN_CENTER
    return elem_sprites

  def view_elems(view, elems, hero=None, visited_cells=None):

    def is_elem_visible(elem):
      if next((a for g in view.anims for a in g if a.target is elem), None):
        return True

      if view.transitioning and not isinstance(elem, Door):
        return False

      if not view.stage.is_overworld and hero and elem.cell not in hero.visible_cells:
        return False

      try:
        return (elem.rect and view.camera.rect.colliderect(elem.rect)
          or view.camera.rect.colliderect(elem.image.get_rect(midbottom=elem.pos)))
      except AttributeError:
        return view.camera.rect.collidepoint(elem.pos)

    elems = [*filter(is_elem_visible, elems)]
    return [s for e in elems for s in view.view_elem(elem=e, visited_cells=visited_cells)]

  def view_vfx(view, vfx):
    return [s for v in vfx for s in v.view()]

  def view(view, hero, visited_cells):
    sprites = []

    stage = view.stage
    sprites += view.view_elems(stage.elems, hero, visited_cells)
    sprites += view.view_vfx(view.vfx)

    camera_offset = (0, 0)
    if type(view.anim) is ShakeAnim:
      camera_offset = vector.add(camera_offset, (
        view.anim.target
          and (0, view.anim.offset)
          or (view.anim.offset, 0)
      ))

    if not view.camera.rect:
      return []

    camera_pos = vector.negate(view.camera.rect.topleft)
    sprites = Sprite.move_all(
      sprites=[s for s in sprites if s.layer != "ui"],
      offset=vector.add(camera_pos, camera_offset)
    ) + [s for s in sprites if s.layer == "ui"]

    sprites += Sprite.move_all(
      sprites=view.view_tiles(hero, visited_cells),
      offset=camera_offset
    )

    sprites.sort(key=StageView.order)
    return sprites
