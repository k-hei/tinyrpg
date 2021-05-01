import sys
from math import ceil
from pygame import Surface, Rect
from pygame.transform import rotate, flip, scale

from assets import load as use_assets
from filters import replace_color
from palette import BLACK, WHITE, COLOR_WALL, darken
from config import ITEM_OFFSET, TILE_SIZE, DEBUG
from sprite import Sprite
from lib.lerp import lerp

from dungeon.actors import DungeonActor
from dungeon.props.chest import Chest
from dungeon.props.soul import Soul

from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.bounce import BounceAnim
from anims.pause import PauseAnim
from anims.awaken import AwakenAnim
from anims.chest import ChestAnim
from anims.item import ItemAnim

class StageView:
  LAYERS = ["tiles", "elems", "vfx", "numbers", "ui"]

  def order(sprite):
    sprite_x, sprite_y = sprite.pos
    depth = StageView.LAYERS.index(sprite.layer) * 1000
    y = sprite_y + sprite.image.get_height() + sprite.offset
    return depth + y

  def __init__(view, size):
    width, height = size
    width += TILE_SIZE * 2
    height += TILE_SIZE * 2
    view.tile_surface = Surface((width, height)).convert_alpha()
    view.tile_offset = (0, 0)
    view.tile_cache = {}
    view.facings = {}

  def redraw_tiles(view, stage, camera, visible_cells, visited_cells):
    sprites = []
    camera = camera.get_rect()
    start_x = camera.left // TILE_SIZE - 1
    start_y = camera.top // TILE_SIZE - 1
    end_x = ceil(camera.right / TILE_SIZE) + 1
    end_y = ceil(camera.bottom / TILE_SIZE) + 1
    for row in range(start_y, end_y + 1):
      for col in range(start_x, end_x + 1):
        cell = (col, row)
        if cell in visible_cells:
          image = render_tile(stage, cell, visited_cells)
          if not image:
            continue
          image = replace_color(image, WHITE, COLOR_WALL)
          image_darken = replace_color(image, COLOR_WALL, darken(COLOR_WALL))
          view.tile_cache[cell] = image_darken
        elif cell in view.tile_cache:
          image = view.tile_cache[cell]
        else:
          continue
        x = (col - start_x) * TILE_SIZE
        y = (row - start_y) * TILE_SIZE
        sprites.append(Sprite(
          image=image,
          pos=(x, y),
          layer="tiles"
        ))
    view.tile_surface.fill(BLACK)
    view.tile_offset = (start_x, start_y)
    for sprite in sprites:
      view.tile_surface.blit(sprite.image, sprite.pos)

  def draw_tiles(view, surface, camera):
    camera = camera.get_rect()
    offset_x, offset_y = view.tile_offset
    dest_x = -camera.left + offset_x * TILE_SIZE
    dest_y = -camera.top + offset_y * TILE_SIZE
    surface.blit(view.tile_surface, (dest_x, dest_y))

  def render_elem(view, elem, anims, vfx):
    sprites = []
    assets = use_assets()

    col, row = elem.cell
    sprite_x = col * TILE_SIZE
    sprite_y = row * TILE_SIZE
    image = elem.render(anims)
    scale_x = 1
    scale_y = 1
    scale_origin = "center"
    facing_x, facing_y = (0, 0)
    if elem in view.facings:
      facing_x, facing_y = view.facings[elem]
      new_facing_x, _ = elem.facing
      if new_facing_x != 0:
        facing_x = new_facing_x

    if type(elem) is Soul:
      elem.update(vfx)
      pos_x, pos_y = elem.pos
      sprite_x += pos_x
      sprite_y += pos_y

    item = None
    anim_group = anims[0] if anims else []

    for anim in [a for a in anim_group if a.target is elem]:
      if type(anim) is ChestAnim or type(anim) is ItemAnim:
        item = (
          anim.item.render(),
          anim.time / anim.duration,
          elem.cell
        )

      if type(anim) is FlinchAnim:
        offset_x, offset_y = anim.offset
        sprite_x += offset_x
        sprite_y += offset_y

      if type(anim) is BounceAnim:
        scale_x, scale_y = anim.scale
        scale_origin = "bottom"

      if type(anim) is FlickerAnim:
        pinch_duration = anim.duration // 4
        t = max(0, anim.time - anim.duration + pinch_duration) / pinch_duration
        scale_x = lerp(1, 0, t)
        scale_y = lerp(1, 3, t)

      if type(anim) in (AttackAnim, MoveAnim):
        src_x, src_y = anim.src_cell
        dest_x, dest_y = anim.dest_cell
        if dest_x < src_x:
          facing_x = -1
        elif dest_x > src_x:
          facing_y = 1
        col, row = anim.cur_cell
        sprite_x = col * TILE_SIZE
        sprite_y = row * TILE_SIZE

      if anim.done:
        anim_group.remove(anim)

    # HACK: if element will move during the next animation sequence,
    # make sure it doesn't jump ahead to the target position
    for group in anims:
      for anim in group:
        if anims.index(group) == 0:
          continue
        if anim.target is elem and type(anim) is MoveAnim:
          col, row = anim.src_cell
          sprite_x = col * TILE_SIZE
          sprite_y = row * TILE_SIZE

    if isinstance(elem, DungeonActor):
      view.facings[elem] = (facing_x, facing_y)
    if image:
      if facing_x == -1:
        image = flip(image, True, False)
      scaled_image = image
      if scale_x != 1 or scale_y != 1:
        scaled_image = scale(image, (
          round(image.get_width() * scale_x),
          round(image.get_height() * scale_y)
        ))
      x = sprite_x + TILE_SIZE // 2 - scaled_image.get_width() // 2
      y = sprite_y
      if scale_origin == "center":
        y += TILE_SIZE // 2 - scaled_image.get_height() // 2
      else:
        y += TILE_SIZE - scaled_image.get_height()
      sprites.append(Sprite(image=scaled_image, pos=(x, y), layer="elems"))

    if item:
      image, t, (col, row) = item
      sprite_x = col * TILE_SIZE
      sprite_y = row * TILE_SIZE
      offset = min(1, t * 3) * 6 + ITEM_OFFSET
      x = sprite_x + TILE_SIZE // 2 - image.get_width() // 2
      y = sprite_y + TILE_SIZE // 2 - image.get_height() // 2 - offset
      sprites.append(Sprite(image=image, pos=(x, y), layer="numbers"))

    return sprites

  def render_elems(view, elems, camera, visible_cells, anims, vfx):
    sprites = []
    camera = camera.get_rect()
    def is_visible(cell):
      if cell not in visible_cells:
        return False
      x, y = cell
      x *= TILE_SIZE
      y *= TILE_SIZE
      if (x + TILE_SIZE < camera.left
      or y + TILE_SIZE < camera.top
      or x > camera.right
      or y > camera.bottom):
        return False
      return True
    visible_elems = [e for e in elems if is_visible(e.cell)]
    for elem in visible_elems:
      sprites += view.render_elem(elem, anims, vfx)

    anim_group = anims[0] if anims else []
    for anim in anim_group:
      anim.update()
      if type(anim) is PauseAnim and anim is anim_group[0]:
        break

    for anim_group in anims:
      for anim in anim_group:
        if anim.done:
          anim_group.remove(anim)
        elif anim.target and anim.target not in visible_elems:
          anim_group.remove(anim)
        if len(anim_group) == 0:
          anims.remove(anim_group)

    return sprites

  def render_vfx(view, vfx, camera):
    sprites = []
    assets = use_assets()
    for fx in vfx:
      x, y = fx.pos
      if x < camera.left or y < camera.top or x >= camera.right or y >= camera.bottom:
        continue
      frame = fx.update()
      if frame == -1:
        continue
      if fx.done:
        vfx.remove(fx)
        continue
      image = assets.sprites["fx_" + fx.kind + str(frame)]
      if fx.color:
        image = replace_color(image, BLACK, fx.color)
      x += TILE_SIZE // 2 - image.get_width() // 2
      y = y + TILE_SIZE // 2 - image.get_height() // 2
      sprites.append(Sprite(image=image, pos=(x, y), layer="vfx"))
    return sprites

  def render_numbers(view, numbers, camera):
    sprites = []
    for number in numbers:
      sprites += number.render()
      if number.done:
        numbers.remove(number)
    return sprites

  def draw_sprites(view, surface, sprites, camera):
    camera_x, camera_y = camera.pos
    for sprite in sprites:
      try:
        sprite_x, sprite_y = sprite.pos
        sprite_x -= camera_x
        sprite_y -= camera_y
        surface.blit(sprite.image, (sprite_x, sprite_y))
      except:
        print("[DEBUG] Failed to draw sprite of layer '{}'".format(sprite.layer),
          "and pos '{}':".format(sprite.pos),
          sys.exc_info()[0].with_traceback())

  def draw(view, surface, ctx):
    visible_cells = ctx.hero.visible_cells
    visited_cells = ctx.get_visited_cells()
    camera = ctx.camera
    anims = ctx.anims
    vfx = ctx.vfx
    numbers = ctx.numbers
    stage = ctx.floor
    elems = stage.elems
    sprites = [*stage.decors]
    sprites += view.render_elems(elems, camera, visible_cells, anims, vfx)
    sprites += view.render_vfx(vfx, camera)
    sprites += view.render_numbers(numbers, camera)
    sprites.sort(key=StageView.order)
    view.draw_tiles(surface, camera)
    view.draw_sprites(surface, sprites, camera)

def render_tile(stage, cell, visited_cells=[]):
  assets = use_assets()
  x, y = cell
  sprite_name = None
  tile = stage.get_tile_at(cell)
  tile_above = stage.get_tile_at((x, y - 1))
  tile_below = stage.get_tile_at((x, y + 1))
  tile_nw = stage.get_tile_at((x - 1, y - 1))
  tile_ne = stage.get_tile_at((x + 1, y - 1))
  tile_sw = stage.get_tile_at((x - 1, y + 1))
  tile_se = stage.get_tile_at((x + 1, y + 1))
  if tile is stage.WALL or tile is stage.DOOR_HIDDEN or (
  tile is stage.DOOR_WAY and tile_below is stage.DOOR_HIDDEN):
    if tile_below is stage.FLOOR or tile_below is stage.PIT:
      if x % (3 + y % 2) == 0:
        sprite_name = "wall_torch"
      else:
        sprite_name = "wall_base"
    else:
      return render_wall(stage, cell, visited_cells)
  elif tile is stage.STAIRS_UP:
    sprite_name = "stairs_up"
  elif tile is stage.STAIRS_DOWN:
    sprite_name = "stairs_down"
  elif tile is stage.DOOR:
    sprite_name = "door"
  elif tile is stage.DOOR_OPEN:
    sprite_name = "door_open"
  elif tile is stage.DOOR_LOCKED:
    sprite_name = "door"
  elif tile is stage.FLOOR and tile_below is not stage.DOOR:
    sprite_name = "floor"
  elif tile is stage.PIT and tile_above and tile_above is not stage.PIT:
    sprite_name = "pit"
  elif tile is stage.MONSTER_DEN:
    sprite_name = "floor"
  elif tile is stage.COFFIN:
    sprite_name = "coffin"
  elif tile is stage.OASIS:
    return render_oasis(stage, cell)
  return assets.sprites[sprite_name] if sprite_name is not None else None

def render_wall(stage, cell, visited_cells=[]):
  assets = use_assets()
  x, y = cell
  is_wall = lambda x, y: (
    (x, y) not in visited_cells
    or stage.get_tile_at((x, y)) is None
    or stage.get_tile_at((x, y)) is stage.WALL
    or stage.get_tile_at((x, y)) is stage.DOOR_HIDDEN
    or stage.get_tile_at((x, y)) is stage.DOOR_WAY and (is_wall(x, y - 1) or is_wall(x, y + 1))
  )
  is_door = lambda x, y: (
    stage.get_tile_at((x, y)) is stage.DOOR
    or stage.get_tile_at((x, y)) is stage.DOOR_OPEN
    or stage.get_tile_at((x, y)) is stage.DOOR_LOCKED
  )

  sprite = Surface((TILE_SIZE, TILE_SIZE)).convert_alpha()
  sprite.fill(BLACK)

  edge_left = assets.sprites["wall_edge"]
  if "wall_edge_bottom" not in assets.sprites:
    assets.sprites["wall_edge_bottom"] = rotate(edge_left, 90)
  edge_bottom = assets.sprites["wall_edge_bottom"]
  if "wall_edge_right" not in assets.sprites:
    assets.sprites["wall_edge_right"] = rotate(edge_left, 180)
  edge_top = assets.sprites["wall_edge_right"]
  if "wall_edge_top" not in assets.sprites:
    assets.sprites["wall_edge_top"] = rotate(edge_left, 270)
  edge_top = assets.sprites["wall_edge_top"]

  corner_nw = assets.sprites["wall_corner"]
  if "wall_corner_sw" not in assets.sprites:
    assets.sprites["wall_corner_sw"] = rotate(corner_nw, 90)
  corner_sw = assets.sprites["wall_corner_sw"]
  if "wall_corner_se" not in assets.sprites:
    assets.sprites["wall_corner_se"] = rotate(corner_nw, 180)
  corner_se = assets.sprites["wall_corner_se"]
  if "wall_corner_ne" not in assets.sprites:
    assets.sprites["wall_corner_ne"] = rotate(corner_nw, 270)
  corner_ne = assets.sprites["wall_corner_ne"]

  edge_right = rotate(edge_left, 180)
  link = assets.sprites["wall_link"]

  if not is_wall(x - 1, y) or not is_wall(x - 1, y + 1):
    sprite.blit(edge_left, (0, 0))
    if is_wall(x, y - 1):
      sprite.blit(link, (0, 0))
    if is_wall(x, y + 1) and (is_wall(x, y + 2) or is_door(x, y + 2)):
      sprite.blit(flip(link, False, True), (0, 0))

  if not is_wall(x + 1, y) or not is_wall(x + 1, y + 1):
    sprite.blit(edge_right, (0, 0))
    if is_wall(x, y - 1):
      sprite.blit(flip(link, True, False), (0, 0))
    if is_wall(x, y + 1) and (is_wall(x, y + 2) or is_door(x, y + 2)):
      sprite.blit(flip(link, True, True), (0, 0))

  if not is_wall(x, y - 1):
    sprite.blit(edge_top, (0, 0))

  if not is_wall(x, y + 2) and not is_door(x, y + 2) or is_door(x, y + 1):
    sprite.blit(edge_bottom, (0, 0))

  if not is_wall(x, y - 1) and is_wall(x - 1, y):
    sprite.blit(rotate(flip(link, False, True), -90), (0, 0))

  if not is_wall(x, y - 1) and is_wall(x + 1, y):
    sprite.blit(rotate(link, -90), (0, 0))

  if (not is_wall(x - 1, y - 1) and is_wall(x - 1, y) and is_wall(x, y - 1)
  or not is_wall(x - 1, y - 1) and not is_wall(x, y - 1) and not is_wall(x - 1, y)):
    sprite.blit(corner_nw, (0, 0))

  if (not is_wall(x + 1, y - 1) and is_wall(x + 1, y) and is_wall(x, y - 1)
  or not is_wall(x + 1, y - 1) and not is_wall(x, y - 1) and not is_wall(x + 1, y)):
    sprite.blit(corner_ne, (0, 0))

  if ((not is_wall(x - 1, y + 2) and not is_door(x - 1, y + 2)) and is_wall(x - 1, y + 1) and is_wall(x - 1, y) and (is_wall(x, y + 2) or is_door(x, y + 2))
  or is_wall(x, y + 1) and not is_wall(x - 1, y + 1) and not is_wall(x, y + 2) and (not is_door(x, y + 2) or is_wall(x - 1, y))
  or is_door(x, y + 1) and (not is_wall(x - 1, y) or not is_wall(x - 1, y + 1))):
    sprite.blit(corner_sw, (0, 0))

  if ((not is_wall(x + 1, y + 2) and not is_door(x + 1, y + 2)) and is_wall(x + 1, y + 1) and is_wall(x + 1, y) and (is_wall(x, y + 2) or is_door(x, y + 2))
  or is_wall(x, y + 1) and not is_wall(x + 1, y + 1) and not is_wall(x, y + 2) and (not is_door(x, y + 2) or is_wall(x + 1, y))
  or is_door(x, y + 1) and (not is_wall(x + 1, y) or not is_wall(x + 1, y + 1))):
    sprite.blit(corner_se, (0, 0))

  if is_wall(x - 1, y) and (not is_wall(x, y + 2) and not is_door(x, y + 2) or is_door(x, y + 1) and is_wall(x - 1, y + 1)):
    sprite.blit(rotate(link, 90), (0, 0))

  if is_wall(x + 1, y) and (not is_wall(x, y + 2) and not is_door(x, y + 2) or is_door(x, y + 1) and is_wall(x + 1, y + 1)):
    sprite.blit(rotate(flip(link, True, False), -90), (0, 0))

  return sprite

def render_oasis(stage, cell):
  sprites = use_assets().sprites
  x, y = cell
  o = lambda x, y: stage.get_tile_at((x, y)) is stage.OASIS
  if o(x, y - 1) and o(x, y + 1) and not o(x - 1, y):
    return sprites["oasis_edge"]
  elif o(x, y - 1) and o(x, y + 1) and not o(x + 1, y):
    return flip(sprites["oasis_edge"], True, False)
  if o(x - 1, y) and o(x + 1, y) and not o(x, y - 1):
    return sprites["oasis_stairs"]
  elif o(x - 1, y) and o(x + 1, y) and not o(x, y + 1):
    return sprites["oasis_edge_bottom"]
  elif o(x + 1, y) and o(x, y + 1) and not o(x - 1, y - 1):
    return sprites["oasis_corner_top"]
  elif o(x - 1, y) and o(x, y + 1) and not o(x + 1, y - 1):
    return flip(sprites["oasis_corner_top"], True, False)
  elif o(x + 1, y) and o(x, y - 1) and not o(x - 1, y + 1):
    return sprites["oasis_corner_bottom"]
  elif o(x - 1, y) and o(x, y - 1) and not o(x + 1, y + 1):
    return flip(sprites["oasis_corner_bottom"], True, False)
