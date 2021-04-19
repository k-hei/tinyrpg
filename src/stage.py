from dataclasses import dataclass

import math
import pygame
import config
import palette
from assets import load as use_assets
from filters import replace_color

from actors import Actor
from actors.knight import Knight
from actors.mage import Mage
from actors.eye import Eye
from actors.mimic import Mimic
from actors.npc import NPC

from props.chest import Chest
from props.soul import Soul

from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.pause import PauseAnim
from anims.awaken import AwakenAnim
from anims.chest import ChestAnim
from lerp import lerp

@dataclass
class Tile:
  solid: bool
  opaque: bool
  pit: bool

class Stage:
  FLOOR = Tile(solid=False, opaque=False, pit=False)
  WALL = Tile(solid=True, opaque=True, pit=False)
  PIT = Tile(solid=True, opaque=False, pit=True)
  DOOR = Tile(solid=True, opaque=True, pit=False)
  DOOR_OPEN = Tile(solid=False, opaque=False, pit=False)
  DOOR_HIDDEN = Tile(solid=True, opaque=True, pit=False)
  DOOR_LOCKED = Tile(solid=True, opaque=True, pit=False)
  STAIRS_UP = Tile(solid=False, opaque=False, pit=False)
  STAIRS_DOWN = Tile(solid=False, opaque=False, pit=False)
  MONSTER_DEN = Tile(solid=False, opaque=False, pit=False)

  def __init__(stage, size):
    (width, height) = size
    stage.size = size
    stage.data = [Stage.FLOOR] * (width * height)
    stage.elems = []
    stage.rooms = []
    stage.entrance = None
    stage.stairs = None
    stage.trap_sprung = False
    stage.facings = {}

  def fill(stage, data):
    (width, height) = stage.size
    for i in range(width * height):
      stage.data[i] = data

  def get_cells(stage):
    width, height = stage.size
    cells = []
    for y in range(height):
      for x in range(width):
        cells.append((x, y))
    return cells

  def is_cell_empty(stage, cell):
    if stage.get_tile_at(cell).solid:
      return False
    if stage.get_elem_at(cell):
      return False
    return True

  def get_elem_at(stage, cell):
    return next((e for e in stage.elems if e.cell == cell), None)

  def get_tile_at(stage, cell):
    if not stage.contains(cell):
      return None
    width = stage.size[0]
    x, y = cell
    return stage.data[y * width + x]

  def set_tile_at(stage, cell, data):
    if not stage.contains(cell):
      return
    width = stage.size[0]
    x, y = cell
    stage.data[y * width + x] = data

  def find_tile(stage, tile):
    width, height = stage.size
    for y in range(height):
      for x in range(width):
        cell = (x, y)
        if stage.get_tile_at(cell) is tile:
          return cell
    return None

  def spawn_elem(stage, elem, cell=None):
    stage.elems.append(elem)
    if cell:
      elem.cell = cell

  def remove_elem(stage, elem):
    if elem in stage.elems:
      stage.elems.remove(elem)
      elem.cell = None

  def contains(stage, cell):
    (width, height) = stage.size
    (x, y) = cell
    return x >= 0 and y >= 0 and x < width and y < height

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
      x += config.TILE_SIZE // 2 - sprite.get_width() // 2
      x += -round(camera_x)
      y = y + config.TILE_SIZE // 2 - sprite.get_height() // 2
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
      # HACK: update move and attack separately in an attempt to reduce jitter (doesn't work)
      if type(anim) not in (MoveAnim, AttackAnim):
        anim.update()

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

    (col, row) = elem.cell
    sprite = elem.render(anims)
    sprite_x = col * config.TILE_SIZE
    sprite_y = row * config.TILE_SIZE
    scale_x = 1
    scale_y = 1

    if type(elem) is Soul:
      elem.update(vfx)
      pos_x, pos_y = elem.pos
      sprite_x += pos_x
      sprite_y += pos_y

    item = None
    anim_group = anims[0] if anims else []
    pausing = next((a for a in anim_group if type(a) is PauseAnim), None)

    for anim in [a for a in anim_group if a.target is elem]:
      if type(anim) is ChestAnim:
        item = (
          anim.item.render(),
          anim.time / anim.duration,
          elem.cell
        )

      if type(anim) is FlinchAnim:
        sprite_x += anim.x

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
        col, row = anim.update()
        sprite_x = col * config.TILE_SIZE
        sprite_y = row * config.TILE_SIZE

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
          sprite_x = col * config.TILE_SIZE
          sprite_y = row * config.TILE_SIZE

    if isinstance(elem, Actor):
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
      x = sprite_x + config.TILE_SIZE // 2 - scaled_sprite.get_width() // 2 - round(camera_x)
      y = sprite_y + config.TILE_SIZE // 2 - scaled_sprite.get_height() // 2 - round(camera_y)
      surface.blit(scaled_sprite, (x, y))

    if item:
      sprite, t, (col, row) = item
      sprite_x = col * config.TILE_SIZE
      sprite_y = row * config.TILE_SIZE
      offset = min(1, t * 3) * 6 + 8
      x = sprite_x + config.TILE_SIZE // 2 - sprite.get_width() // 2 - round(camera_x)
      y = sprite_y + config.TILE_SIZE // 2 - sprite.get_height() // 2 - round(camera_y) - offset
      surface.blit(sprite, (x, y))

  def draw_tiles(stage, surface, visible_cells=None, visited_cells=[], camera_pos=None):
    camera_x, camera_y = (0, 0)
    if camera_pos:
      camera_x, camera_y = camera_pos

    if visible_cells is None:
      visible_cells = stage.get_cells()

    for cell in visited_cells:
      col, row = cell
      sprite = stage.render_tile(cell)
      if sprite is None:
        continue
      if cell not in visible_cells:
        sprite = replace_color(sprite, palette.WHITE, palette.GRAY)
      x = col * config.TILE_SIZE - round(camera_x)
      y = row * config.TILE_SIZE - round(camera_y)
      surface.blit(sprite, (x, y))

  def render_tile(stage, cell):
    assets = use_assets()
    x, y = cell
    sprite_name = None
    tile = stage.get_tile_at(cell)
    tile_above = stage.get_tile_at((x, y - 1))
    tile_below = stage.get_tile_at((x, y + 1))
    if tile is Stage.WALL or tile is Stage.DOOR_HIDDEN:
      if tile_below is Stage.FLOOR or tile_below is Stage.PIT:
        sprite_name = "wall_base"
      else:
        sprite_name = "wall"
    elif tile is Stage.STAIRS_UP:
      sprite_name = "stairs_up"
    elif tile is Stage.STAIRS_DOWN:
      sprite_name = "stairs_down"
    elif tile is Stage.DOOR:
      sprite_name = "door"
    elif tile is Stage.DOOR_OPEN:
      sprite_name = "door_open"
    elif tile is Stage.DOOR_LOCKED:
      sprite_name = "door"
    elif tile is Stage.FLOOR:
      sprite_name = "floor"
    elif tile is Stage.PIT and tile_above and tile_above is not Stage.PIT:
      sprite_name = "pit"
    elif tile is Stage.MONSTER_DEN:
      sprite_name = "floor"
    if sprite_name is not None:
      return assets.sprites[sprite_name]
    else:
      return None
