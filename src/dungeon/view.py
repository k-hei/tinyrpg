import math
import pygame
from pygame import Surface, Rect
from pygame.transform import rotate, flip
import palette
from assets import load as use_assets
from filters import replace_color
from config import ITEM_OFFSET, TILE_SIZE, DEBUG

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

class View:
  def draw(stage, surface, ctx):
    visible_cells = ctx.hero.visible_cells
    visited_cells = next((cells for floor, cells in ctx.memory if floor is ctx.floor), None)
    anims = ctx.anims
    camera_pos = ctx.camera.pos
    stage.draw_tiles(surface, visible_cells, visited_cells, camera_pos)
    stage.draw_elems(surface, visible_cells, anims, ctx.vfx, camera_pos)
    stage.draw_vfx(surface, ctx.vfx, camera_pos)
    stage.draw_numbers(surface, ctx.numbers, camera_pos)

  def draw_numbers(stage, surface, numbers, camera_pos):
    for value in numbers:
      value.draw(surface, camera_pos)
      if value.done:
        numbers.remove(value)

  def draw_vfx(stage, surface, vfx, camera_pos):
    assets = use_assets()
    for fx in vfx:
      x, y = fx.pos
      camera_x, camera_y = camera_pos
      frame = fx.update()
      if frame == -1:
        continue
      if fx.done:
        vfx.remove(fx)
        continue
      sprite = assets.sprites["fx_" + fx.kind + str(frame)]
      if fx.color:
        sprite = replace_color(sprite, palette.BLACK, fx.color)
      x += TILE_SIZE // 2 - sprite.get_width() // 2
      x += -round(camera_x)
      y = y + TILE_SIZE // 2 - sprite.get_height() // 2
      y += -round(camera_y)
      surface.blit(sprite, (x, y))

  def draw_elems(stage, surface, visible_cells, anims, vfx, camera_pos):
    camera_x, camera_y = camera_pos

    if visible_cells is None:
      visible_cells = stage.get_cells()

    # depthsort by y position
    stage.elems.sort(key=lambda elem: elem.cell[1] + (100 if type(elem) is Soul else 0))

    visible_elems = [e for e in stage.elems if e.cell in visible_cells]
    for elem in visible_elems:
      sprite = stage.draw_elem(elem, surface, anims, vfx, camera_pos)

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

  def draw_elem(stage, elem, surface, anims, vfx, camera_pos=(0, 0)):
    assets = use_assets()
    camera_x, camera_y = camera_pos

    facing_x, facing_y = (0, 0)
    if elem in stage.facings:
      facing_x, facing_y = stage.facings[elem]
      new_facing_x, _ = elem.facing
      if new_facing_x != 0:
        facing_x = new_facing_x

    col, row = elem.cell
    sprite = elem.render(anims)
    sprite_x = col * TILE_SIZE
    sprite_y = row * TILE_SIZE
    scale_x = 1
    scale_y = 1
    scale_origin = "center"

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
    if sprite:
      if facing_x == -1:
        sprite = pygame.transform.flip(sprite, True, False)
      scaled_sprite = sprite
      if scale_x != 1 or scale_y != 1:
        scaled_sprite = pygame.transform.scale(sprite, (
          round(sprite.get_width() * scale_x),
          round(sprite.get_height() * scale_y)
        ))
      x = sprite_x - round(camera_x) + TILE_SIZE // 2 - scaled_sprite.get_width() // 2
      y = sprite_y - round(camera_y)
      if scale_origin == "center":
        y += TILE_SIZE // 2 - scaled_sprite.get_height() // 2
      else:
        y += TILE_SIZE - scaled_sprite.get_height()
      surface.blit(scaled_sprite, (x, y))

    if item:
      sprite, t, (col, row) = item
      sprite_x = col * TILE_SIZE
      sprite_y = row * TILE_SIZE
      offset = min(1, t * 3) * 6 + ITEM_OFFSET
      x = sprite_x + TILE_SIZE // 2 - sprite.get_width() // 2 - round(camera_x)
      y = sprite_y + TILE_SIZE // 2 - sprite.get_height() // 2 - round(camera_y) - offset
      surface.blit(sprite, (x, y))

  def draw_tiles(stage, surface, visible_cells=None, visited_cells=[], camera_pos=None):
    camera_x, camera_y = (0, 0)
    if camera_pos:
      camera_x, camera_y = camera_pos

    if visible_cells is None:
      visible_cells = stage.get_cells()

    for cell in visited_cells:
      col, row = cell
      x = col * TILE_SIZE - round(camera_x)
      y = row * TILE_SIZE - round(camera_y)
      if (x <= -TILE_SIZE
      or y <= -TILE_SIZE
      or x >= surface.get_width()
      or y >= surface.get_height()):
        continue
      sprite = stage.render_tile(cell, visited_cells)
      if sprite is None:
        continue
      if cell not in visible_cells:
        sprite = replace_color(sprite, palette.WHITE, palette.GOLD_DARK)
      elif not DEBUG:
        sprite = replace_color(sprite, palette.WHITE, palette.SAFFRON)
      surface.blit(sprite, (x, y))

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
        return stage.render_wall(stage, cell, visited_cells)
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
      return stage.render_oasis(cell)
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

    CORNER_SIZE = 7
    edge = assets.sprites["wall_edge"]
    link = assets.sprites["wall_link"]

    if not is_wall(x - 1, y) or not is_wall(x - 1, y + 1):
      sprite.blit(edge, (0, 0))
      if is_wall(x, y - 1):
        sprite.blit(link, (0, 0))
      if is_wall(x, y + 1) and (is_wall(x, y + 2) or is_door(x, y + 2)):
        sprite.blit(flip(link, False, True), (0, 0))

    if not is_wall(x + 1, y) or not is_wall(x + 1, y + 1):
      sprite.blit(rotate(edge, 180), (0, 0))
      if is_wall(x, y - 1):
        sprite.blit(flip(link, True, False), (0, 0))
      if is_wall(x, y + 1) and (is_wall(x, y + 2) or is_door(x, y + 2)):
        sprite.blit(flip(link, True, True), (0, 0))

    if not is_wall(x, y - 1):
      sprite.blit(rotate(edge, -90), (0, 0))

    if not is_wall(x, y + 2) and not is_door(x, y + 2) or is_door(x, y + 1):
      sprite.blit(rotate(edge, 90), (0, 0))

    if not is_wall(x, y - 1) and is_wall(x - 1, y):
      sprite.blit(rotate(flip(link, False, True), -90), (0, 0))

    if not is_wall(x, y - 1) and is_wall(x + 1, y):
      sprite.blit(rotate(link, -90), (0, 0))

    if (not is_wall(x - 1, y - 1) and is_wall(x - 1, y) and is_wall(x, y - 1)
    or not is_wall(x - 1, y - 1) and not is_wall(x, y - 1) and not is_wall(x - 1, y)):
      draw_corner(sprite, 1, 1)

    if (not is_wall(x + 1, y - 1) and is_wall(x + 1, y) and is_wall(x, y - 1)
    or not is_wall(x + 1, y - 1) and not is_wall(x, y - 1) and not is_wall(x + 1, y)):
      draw_corner(sprite, TILE_SIZE - CORNER_SIZE - 1, 1)

    if ((not is_wall(x - 1, y + 2) and not is_door(x - 1, y + 2)) and is_wall(x - 1, y + 1) and is_wall(x - 1, y) and (is_wall(x, y + 2) or is_door(x, y + 2))
    or is_wall(x, y + 1) and not is_wall(x - 1, y + 1) and not is_wall(x, y + 2) and (not is_door(x, y + 2) or is_wall(x - 1, y))
    or is_door(x, y + 1) and (not is_wall(x - 1, y) or not is_wall(x - 1, y + 1))):
      draw_corner(sprite, 1, TILE_SIZE - CORNER_SIZE - 1)

    if ((not is_wall(x + 1, y + 2) and not is_door(x + 1, y + 2)) and is_wall(x + 1, y + 1) and is_wall(x + 1, y) and (is_wall(x, y + 2) or is_door(x, y + 2))
    or is_wall(x, y + 1) and not is_wall(x + 1, y + 1) and not is_wall(x, y + 2) and (not is_door(x, y + 2) or is_wall(x + 1, y))
    or is_door(x, y + 1) and (not is_wall(x + 1, y) or not is_wall(x + 1, y + 1))):
      draw_corner(sprite, TILE_SIZE - CORNER_SIZE - 1, TILE_SIZE - CORNER_SIZE - 1)

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


def draw_corner(sprite, x, y):
  CORNER_SIZE = 7
  pygame.draw.rect(sprite, palette.BLACK, Rect(x - 1, y - 1, CORNER_SIZE + 2, CORNER_SIZE + 2))
  pygame.draw.rect(sprite, palette.WHITE, Rect(x, y, CORNER_SIZE, CORNER_SIZE), width=1)
