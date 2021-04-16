from dataclasses import dataclass

import math
import pygame
import config
import palette
from assets import load as use_assets
from filters import replace_color

from actors.knight import Knight
from actors.mage import Mage
from actors.eye import Eye
from actors.mimic import Mimic
from actors.chest import Chest
from actors.npc import NPC

from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.shake import ShakeAnim
from anims.flicker import FlickerAnim
from anims.pause import PauseAnim
from anims.awaken import AwakenAnim
from anims.chest import ChestAnim

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
    stage.actors = []
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
    if stage.get_actor_at(cell):
      return False
    return True

  def get_actor_at(stage, cell):
    return next((actor for actor in stage.actors if actor.cell == cell), None)

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

  def spawn_actor(stage, actor, cell=None):
    stage.actors.append(actor)
    if cell:
      actor.cell = cell

  def remove_actor(stage, actor):
    if actor in stage.actors:
      stage.actors.remove(actor)
      actor.cell = None

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
    stage.draw_actors(surface, visible_cells, anims, camera_pos)
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
      kind, cell, anim = fx
      col, row = cell
      camera_x, camera_y = camera_pos
      frame = anim.update()
      if frame == -1:
        continue
      if anim.done:
        vfx.remove(fx)
        continue
      sprite = assets.sprites["fx_" + kind + str(frame)]
      x = col * config.tile_size
      x += config.tile_size // 2 - sprite.get_width() // 2
      x += -round(camera_x)
      y = row * config.tile_size
      y = y + config.tile_size // 2 - sprite.get_height() // 2
      y += -round(camera_y)
      surface.blit(sprite, (x, y))

  def draw_actors(stage, surface, visible_cells=None, anims=[], camera_pos=(0, 0)):
    camera_x, camera_y = camera_pos

    if visible_cells is None:
      visible_cells = stage.get_cells()

    stage.actors.sort(key=lambda actor: actor.cell[1])
    visible_actors = [actor for actor in stage.actors if actor.cell in visible_cells]
    for actor in visible_actors:
      sprite = stage.draw_actor(actor, surface, anims, camera_pos)

    for group in anims:
      for anim in group:
        if anim.target is not None and anim.target not in visible_actors:
          group.remove(anim)
          if len(group) == 0:
            anims.remove(group)

  def draw_actor(stage, actor, surface, anims, camera_pos=(0, 0)):
    assets = use_assets()
    camera_x, camera_y = camera_pos

    facing_x, facing_y = (0, 0)
    if actor in stage.facings:
      facing_x, facing_y = stage.facings[actor]
      new_facing_x, _ = actor.facing
      if new_facing_x != 0:
        facing_x = new_facing_x

    (col, row) = actor.cell
    sprite_x = col * config.tile_size
    sprite_y = row * config.tile_size
    sprite = None
    if type(actor) is Knight:
      sprite = assets.sprites["knight"]
      if actor.asleep:
        sprite = replace_color(sprite, palette.BLUE, palette.PURPLE)
    elif type(actor) is Mage:
      sprite = assets.sprites["mage"]
    elif type(actor) is Eye:
      sprite = assets.sprites["eye"]
      if actor.asleep:
        sprite = assets.sprites["eye_attack"]
    elif type(actor) is Chest:
      if actor.opened:
        sprite = assets.sprites["chest_open"]
      else:
        sprite = assets.sprites["chest"]
    elif type(actor) is Mimic:
      sprite = assets.sprites["chest"]
      if not actor.idle:
        sprite = replace_color(sprite, palette.GOLD, palette.RED)
    elif type(actor) is NPC:
      sprite = assets.sprites["eye"]
      sprite = replace_color(sprite, palette.RED, (0x37, 0x94, 0x6E))

    item = None
    anim_group = anims[0] if len(anims) else []
    pause = next((anim for anim in anim_group if type(anim) is PauseAnim), None)

    for anim in anim_group:
      if anim.target is not actor:
        continue

      if type(anim) is ChestAnim:
        frame = anim.update() + 1
        sprite = assets.sprites["chest_open" + str(frame)]
        item = (
          anim.item.render(),
          anim.time / anim.duration,
          actor.cell
        )

      if type(anim) is MoveAnim:
        if anim.time % (anim.duration // 2) >= anim.duration // 4:
          if type(actor) is Knight:
            sprite = assets.sprites["knight_walk"]
          elif type(actor) is Mage:
            sprite = assets.sprites["mage_walk"]
        if type(actor) is Eye:
          sprite = assets.sprites["eye_attack"]

      if type(anim) is ShakeAnim:
        sprite_x += anim.update()

      flinch_anim = next((a for a in anim_group if type(a) is ShakeAnim and a.target is anim.target), None)
      if type(anim) is ShakeAnim or flinch_anim:
        if anim is flinch_anim and anim.time <= 1:
          sprite = None
        elif type(actor) is Knight:
          sprite = assets.sprites["knight_flinch"]
        elif type(actor) is Mage:
          sprite = assets.sprites["mage_flinch"]
        elif type(actor) is Eye:
          sprite = assets.sprites["eye_flinch"]
          will_awaken = next((anim for anim in anim_group if type(anim) is AwakenAnim), None)
          if will_awaken:
            sprite = replace_color(surface=sprite, old_color=palette.RED, new_color=palette.PURPLE)

      if type(anim) is FlickerAnim:
        visible = anim.update()
        if type(actor) is Mimic and not actor.dead:
          if not visible:
            sprite = replace_color(sprite, palette.GOLD, palette.RED)
        elif not visible:
          sprite = None
        elif type(actor) is Knight:
          sprite = assets.sprites["knight_flinch"]
        elif type(actor) is Eye:
          sprite = assets.sprites["eye_flinch"]

      if type(anim) is AwakenAnim and len(anim_group) == 1:
        recolored = anim.update()
        if recolored and sprite:
          if type(actor) is Mimic:
            sprite = replace_color(surface=sprite, old_color=palette.YELLOW, new_color=palette.PURPLE)
          else:
            sprite = replace_color(surface=sprite, old_color=palette.RED, new_color=palette.PURPLE)

      if type(anim) is AttackAnim:
        if type(actor) is Knight:
          sprite = assets.sprites["knight_walk"]
        elif type(actor) is Mage:
          sprite = assets.sprites["mage_walk"]
        elif type(actor) is Eye:
          sprite = assets.sprites["eye_attack"]

      if type(anim) in (AttackAnim, MoveAnim):
        src_x, src_y = anim.src_cell
        dest_x, dest_y = anim.dest_cell
        if dest_x < src_x:
          facing_x = -1
        elif dest_x > src_x:
          facing_y = 1
        col, row = anim.update()
        sprite_x = col * config.tile_size
        sprite_y = row * config.tile_size

      if anim.done:
        anim_group.remove(anim)

    if actor.asleep and sprite:
      sprite = replace_color(surface=sprite, old_color=palette.RED, new_color=palette.PURPLE)

    for group in anims:
      for anim in group:
        if group is anim_group:
          continue
        if anim.target is actor and type(anim) is MoveAnim:
          col, row = anim.src_cell
          sprite_x = col * config.tile_size
          sprite_y = row * config.tile_size

    stage.facings[actor] = (facing_x, facing_y)
    if sprite:
      flipped = facing_x == -1
      # if type(actor) is Mimic and not actor.idle:
      #   flipped = not flipped
      sprite = pygame.transform.flip(sprite, flipped, False)
      x = sprite_x - round(camera_x)
      y = sprite_y - round(camera_y)
      surface.blit(sprite, (x, y))

    if item:
      sprite, t, (col, row) = item
      sprite_x = (col + 0.5) * config.tile_size
      sprite_y = (row + 0.5) * config.tile_size
      offset = min(1, t * 3) * 6 + 8
      x = sprite_x - sprite.get_width() // 2 - round(camera_x)
      y = sprite_y - sprite.get_height() // 2 - round(camera_y) - offset
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
      x = col * config.tile_size - round(camera_x)
      y = row * config.tile_size - round(camera_y)
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
