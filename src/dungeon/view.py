import math
import pygame
from pygame import Surface, Rect
from pygame.transform import rotate, flip, scale
import palette
from assets import load as use_assets
from filters import replace_color
from config import ITEM_OFFSET, TILE_SIZE, DEBUG
from sprite import Sprite

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
from lib.lerp import lerp

LAYER_ORDER = ["tiles", "elems", "vfx", "numbers", "ui"]

def order(sprite):
  sprite_x, sprite_y = sprite.pos
  y = sprite_y + sprite.image.get_height()
  return LAYER_ORDER.index(sprite.layer) * 1000 + y + sprite.offset

def draw(stage, surface, ctx, tile_surface=None):
  visible_cells = ctx.hero.visible_cells
  visited_cells = next((cells for floor, cells in ctx.memory if floor is ctx.floor), None)

  camera = ctx.camera
  camera_x, camera_y = camera.pos
  camera_x = round(camera_x)
  camera_y = round(camera_y)
  rect = Rect(
    (camera_x, camera_y),
    (surface.get_width(), surface.get_height())
  )

  sprites = []
  if tile_surface is None:
    sprites += render_tiles(stage)
  sprites += render_elems(stage, rect, visible_cells, ctx.anims, ctx.vfx)
  sprites += render_vfx(stage, rect, ctx.vfx)
  sprites += render_numbers(stage, ctx.numbers)
  sprites += stage.decors
  sprites.sort(key=order)

  if tile_surface is None:
    tiles = [s for s in sprites if s.layer == "tiles"]
    stage_width = stage.get_width() * TILE_SIZE
    stage_height = stage.get_height() * TILE_SIZE
    tile_surface = Surface((stage_width, stage_height)).convert_alpha()
    for tile in tiles:
      draw_sprite(tile, tile_surface)
    tile_surface = replace_color(tile_surface, palette.WHITE, palette.SAFFRON)
  surface.blit(tile_surface, (-camera_x, -camera_y))

  for sprite in sprites:
    if sprite.layer == "tiles":
      continue
    draw_sprite(sprite, surface, camera.pos)

  return tile_surface

def draw_sprite(sprite, surface, camera_pos=(0, 0)):
  camera_x, camera_y = camera_pos
  image = sprite.image
  x, y = sprite.pos
  x -= camera_x
  y -= camera_y
  surface.blit(sprite.image, (x, y))

def render_numbers(stage, numbers):
  sprites = []
  for number in numbers:
    sprites += number.render()
    if number.done:
      numbers.remove(number)
  return sprites

def render_vfx(stage, rect, vfx):
  sprites = []
  assets = use_assets()
  for fx in vfx:
    x, y = fx.pos
    if x < rect.left or y < rect.top or x >= rect.right or y >= rect.bottom:
      continue
    frame = fx.update()
    if frame == -1:
      continue
    if fx.done:
      vfx.remove(fx)
      continue
    image = assets.sprites["fx_" + fx.kind + str(frame)]
    if fx.color:
      image = replace_color(image, palette.BLACK, fx.color)
    x += TILE_SIZE // 2 - image.get_width() // 2
    y = y + TILE_SIZE // 2 - image.get_height() // 2
    sprites.append(Sprite(image=image, pos=(x, y), layer="vfx"))
  return sprites

def render_elems(stage, rect, visible_cells, anims, vfx):
  sprites = []
  visible_elems = [e for e in stage.elems if e.cell in visible_cells]
  for elem in visible_elems:
    sprites += render_elem(stage, rect, elem, anims, vfx)

  anim_group = anims[0] if anims else []
  for anim in anim_group:
    anim.update()
    if type(anim) is PauseAnim and anim is anim_group[0]:
      break

  for anim_group in anims:
    for anim in anim_group:
      if anim.done:
        anim_group.remove(anim)
      if anim.target is not None and anim.target not in visible_elems:
        anim_group.remove(anim)
      if len(anim_group) == 0:
        anims.remove(anim_group)
  return sprites

def render_elem(stage, rect, elem, anims, vfx):
  sprites = []
  assets = use_assets()

  col, row = elem.cell
  sprite_x = col * TILE_SIZE
  sprite_y = row * TILE_SIZE
  if (sprite_x + TILE_SIZE < rect.left
  or sprite_y + TILE_SIZE < rect.top
  or sprite_x >= rect.right
  or sprite_y >= rect.bottom):
    return []

  image = elem.render(anims)
  scale_x = 1
  scale_y = 1
  scale_origin = "center"
  facing_x, facing_y = (0, 0)
  if elem in stage.facings:
    facing_x, facing_y = stage.facings[elem]
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
    stage.facings[elem] = (facing_x, facing_y)
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

def render_tiles(stage, visible_cells=None, visited_cells=None, rect=None):
  sprites = []

  if visible_cells is None:
    visible_cells = stage.get_cells()

  if visited_cells is None:
    visited_cells = stage.get_cells()

  for cell in visited_cells:
    col, row = cell
    x = col * TILE_SIZE
    y = row * TILE_SIZE
    if rect and (
    x + TILE_SIZE < rect.left
    or y + TILE_SIZE < rect.top
    or x >= rect.right
    or y >= rect.bottom):
      continue
    tile = stage.get_tile_at(cell)
    image = render_tile(stage, cell, visited_cells)
    if image is None:
      continue
    if cell not in visible_cells:
      image = replace_color(image, palette.WHITE, palette.GOLD_DARK)
    sprites.append(Sprite(image=image, pos=(x, y), layer="tiles"))

  return sprites

def render_tile(stage, cell, visited_cells):
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

def render_wall(stage, cell, visited_cells):
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
  sprite.fill(palette.BLACK)

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
