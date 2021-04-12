from dataclasses import dataclass

import pygame
import config
import palette
from assets import load as use_assets
from filters import replace_color

from actors.knight import Knight
from actors.mage import Mage
from actors.eye import Eye
from actors.chest import Chest

from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.shake import ShakeAnim
from anims.flicker import FlickerAnim
from anims.pause import PauseAnim
from anims.awaken import AwakenAnim

@dataclass
class Tile:
  solid: bool
  opaque: bool

class Stage:
  FLOOR = Tile(solid=False, opaque=False)
  WALL = Tile(solid=True, opaque=True)
  DOOR = Tile(solid=True, opaque=True)
  DOOR_OPEN = Tile(solid=False, opaque=False)
  DOOR_HIDDEN = Tile(solid=True, opaque=True)
  STAIRS_UP = Tile(solid=False, opaque=False)
  STAIRS_DOWN = Tile(solid=False, opaque=False)

  def __init__(stage, size):
    (width, height) = size
    stage.size = size
    stage.data = [Stage.FLOOR] * (width * height)
    stage.actors = []
    stage.rooms = []

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

  def render(stage, surface, ctx):
    visible_cells = ctx.hero.visible_cells
    visited_cells = next((cells for floor, cells in ctx.memory if floor is ctx.floor), None)
    anims = ctx.anims
    camera_pos = ctx.camera.pos
    stage.render_tiles(surface, visible_cells, visited_cells, camera_pos)
    stage.render_actors(surface, visible_cells, anims, camera_pos)

  def render_actors(stage, surface, visible_cells=None, anims=[], camera_pos=(0, 0)):
    camera_x, camera_y = camera_pos

    if visible_cells is None:
      visible_cells = stage.get_cells()

    stage.actors.sort(key=lambda actor: actor.cell[1])
    visible_actors = [actor for actor in stage.actors if actor.cell in visible_cells]
    for actor in visible_actors:
      sprite = stage.render_actor(actor, surface, anims, camera_pos)

  def render_actor(stage, actor, surface, anims, camera_pos=(0, 0)):
    assets = use_assets()
    camera_x, camera_y = camera_pos

    (col, row) = actor.cell
    sprite_x = col * config.tile_size
    sprite_y = row * config.tile_size
    sprite = None
    if type(actor) is Knight:
      sprite = assets.sprites["knight"]
    elif type(actor) is Mage:
      sprite = assets.sprites["mage"]
    elif type(actor) is Eye:
      sprite = assets.sprites["eye"]
    elif type(actor) is Chest:
      if actor.opened:
        sprite = assets.sprites["chest_open"]
      else:
        sprite = assets.sprites["chest"]

    anim_group = anims[0] if len(anims) else []
    for anim in anim_group:
      if anim.target is not actor:
        continue

      if type(anim) is ShakeAnim:
        sprite_x += anim.update()
        if type(actor) is Knight:
          sprite = assets.sprites["knight_flinch"]
        elif type(actor) is Eye:
          sprite = assets.sprites["eye_flinch"]
          will_awaken = next((anim for anim in anim_group if type(anim) is AwakenAnim), None)
          if will_awaken:
            sprite = replace_color(surface=sprite, old_color=palette.RED, new_color=palette.PURPLE)

      if type(anim) is FlickerAnim:
        visible = anim.update()
        if not visible:
          sprite = None
        elif type(actor) is Knight:
          sprite = assets.sprites["knight_flinch"]
        elif type(actor) is Eye:
          sprite = assets.sprites["eye_flinch"]

      if type(anim) is AwakenAnim and len(anim_group) == 1:
        if type(actor) is Eye:
          sprite = assets.sprites["eye_attack"]
        recolored = anim.update()
        if recolored and sprite:
          sprite = replace_color(surface=sprite, old_color=palette.RED, new_color=palette.PURPLE)

      if type(anim) is AttackAnim:
        if type(actor) is Eye:
          sprite = assets.sprites["eye_attack"]

      if type(anim) in (AttackAnim, MoveAnim):
        src_x, src_y = anim.src_cell
        dest_x, dest_y = anim.dest_cell
        if dest_x < src_x:
          facing = -1
        elif dest_x > src_x:
          facing = 1
        col, row = anim.update()
        sprite_x = col * config.tile_size
        sprite_y = row * config.tile_size

      if anim.done:
        anim_group.remove(anim)

    if type(actor) is Eye and actor.asleep and sprite:
      sprite = replace_color(surface=sprite, old_color=palette.RED, new_color=palette.PURPLE)

    for group in anims:
      for anim in group:
        if group is anim_group:
          continue
        if anim.target is actor and type(anim) is MoveAnim:
          col, row = anim.src_cell
          sprite_x = col * config.tile_size
          sprite_y = row * config.tile_size

    facing_x, _ = actor.facing
    if sprite:
      sprite = pygame.transform.flip(sprite, facing_x == -1, False)
      x = sprite_x - round(camera_x)
      y = sprite_y - round(camera_y)
      surface.blit(sprite, (x, y))

  def render_tiles(stage, surface, visible_cells=None, visited_cells=[], camera_pos=None):
    camera_x, camera_y = (0, 0)
    if camera_pos:
      camera_x, camera_y = camera_pos

    if visible_cells is None:
      visible_cells = stage.get_cells()

    for cell in visible_cells:
      col, row = cell
      sprite = stage.render_cell(cell)
      if sprite:
        opacity = 255
        if cell not in visible_cells:
          opacity = 127
        sprite.set_alpha(opacity)
        x = col * config.tile_size - round(camera_x)
        y = row * config.tile_size - round(camera_y)
        surface.blit(sprite, (x, y))
        sprite.set_alpha(None)

  def render_cell(stage, cell):
    assets = use_assets()
    x, y = cell
    sprite_name = None
    tile = stage.get_tile_at(cell)
    if tile is Stage.WALL or tile is Stage.DOOR_HIDDEN:
      if stage.get_tile_at((x, y + 1)) is Stage.FLOOR:
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
    elif tile is Stage.FLOOR:
      sprite_name = "floor"
    if sprite_name is not None:
      return assets.sprites[sprite_name]
    else:
      return None
