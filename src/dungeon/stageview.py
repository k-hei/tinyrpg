import sys
from math import ceil
from pygame import Surface, Rect, SRCALPHA
from pygame.transform import rotate, flip, scale

from assets import load as use_assets
from filters import replace_color, darken
from palette import BLACK, WHITE, COLOR_TILE, darken_color
from config import ITEM_OFFSET, TILE_SIZE, DEBUG
from sprite import Sprite
from lib.lerp import lerp

from dungeon.actors import DungeonActor
from dungeon.props.chest import Chest
from dungeon.props.soul import Soul
from dungeon.props.palm import Palm
from dungeon.props.door import Door

from anims.move import MoveAnim
from anims.jump import JumpAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.bounce import BounceAnim
from anims.pause import PauseAnim
from anims.awaken import AwakenAnim
from anims.chest import ChestAnim
from anims.item import ItemAnim

class StageView:
  LAYERS = ["tiles", "decors", "elems", "vfx", "numbers", "ui"]

  def order(sprite):
    sprite_x, sprite_y = sprite.pos
    try:
      depth = StageView.LAYERS.index(sprite.layer)
    except ValueError:
      depth = 0
    depth *= 1000
    y = sprite_y + sprite.image.get_height() + sprite.offset
    return depth + y

  def __init__(self, size):
    width, height = size
    width += TILE_SIZE * 2
    height += TILE_SIZE * 2
    self.tile_surface = Surface((width, height), SRCALPHA)
    self.tile_offset = (0, 0)
    self.tile_cache = {}
    self.stage = None
    self.facings = {}

  def redraw_tile(self, stage, cell, visited_cells):
    col, row = cell
    start_x, start_y = self.tile_offset
    image = render_tile(stage, cell, visited_cells)
    if not image:
      return
    color = WHITE
    if (stage.get_tile_at(cell) is not stage.OASIS
    and stage.get_tile_at(cell) is not stage.OASIS_STAIRS
    and stage.get_tile_at(cell) is not stage.FLOOR):
      color = COLOR_TILE
      image = replace_color(image, WHITE, color)
    image_darken = image
    if stage.get_tile_at(cell) is not stage.FLOOR:
      image_darken = replace_color(image, color, darken_color(color))
    self.tile_cache[cell] = image_darken
    x = (col - start_x) * TILE_SIZE
    y = (row - start_y) * TILE_SIZE
    self.tile_surface.blit(image, (x, y))

  def redraw_tiles(self, stage, camera, visible_cells, visited_cells):
    sprites = []
    camera = camera.get_rect()
    start_x = camera.left // TILE_SIZE - 1
    start_y = camera.top // TILE_SIZE - 1
    end_x = ceil(camera.right / TILE_SIZE) + 1
    end_y = ceil(camera.bottom / TILE_SIZE) + 1
    self.tile_offset = (start_x, start_y)
    self.tile_surface.fill(BLACK)
    if stage is not self.stage:
      self.stage = stage
      self.tile_cache = {}
    for row in range(start_y, end_y + 1):
      for col in range(start_x, end_x + 1):
        cell = (col, row)
        if cell in visible_cells:
          self.redraw_tile(stage, cell, visited_cells)
        elif cell in self.tile_cache:
          image = self.tile_cache[cell]
          x = (col - start_x) * TILE_SIZE
          y = (row - start_y) * TILE_SIZE
          self.tile_surface.blit(image, (x, y))

  def view_decors(self, decors, camera, visible_cells, visited_cells):
    sprites = []
    for decor in decors:
      if decor.cell not in visited_cells:
        continue
      sprite = decor.sprite.copy()
      if decor.cell not in visible_cells:
        sprite.image = darken(sprite.image)
      sprites.append(sprite)
    return sprites

  def view_elem(self, elem, anims):
    sprites = elem.view(anims)
    if sprites:
      sprite = sprites[0]
      elem_x, elem_y = elem.cell
      sprite.move(((elem_x + 0.5) * TILE_SIZE, (elem_y + 1) * TILE_SIZE))
      sprite.origin = ("center", "bottom")
      return sprites
    else:
      return []

  def view_elems(self, elems, hero, camera, visible_cells, anims):
    sprites = []
    camera = camera.get_rect()
    def is_visible(elem):
      if elem is hero:
        return True
      if elem.cell not in visible_cells:
        return False
      x, y = elem.cell
      x *= TILE_SIZE
      y *= TILE_SIZE
      if (x + TILE_SIZE < camera.left
      or y + TILE_SIZE < camera.top
      or x > camera.right
      or y > camera.bottom):
        return False
      return True
    visible_elems = [e for e in elems if is_visible(e)]
    for elem in visible_elems:
      try:
        sprites += self.view_elem(elem, anims)
      except TypeError:
        print(elem)
        raise

    anim_group = anims[0] if anims else []
    for anim in anim_group:
      anim.update()
      if type(anim) is PauseAnim and anim is anim_group[0]:
        break

    for anim_group in anims:
      for anim in anim_group:
        if not anim or anim.done:
          anim_group.remove(anim)
        elif anim.target and anim.target not in visible_elems:
          anim_group.remove(anim)
        if len(anim_group) == 0:
          anims.remove(anim_group)

    return sprites

  def view_vfx(self, vfx, camera):
    sprites = []
    assets = use_assets()
    camera = camera.get_rect()
    for fx in vfx:
      x, y = fx.pos
      if fx.done:
        vfx.remove(fx)
        continue
      if fx.kind:
        frame = fx.update()
        if frame == -1:
          continue
        image = assets.sprites[frame]
        if fx.color:
          image = replace_color(image, BLACK, fx.color)
      else:
        fx.update()
        image = assets.sprites["fx_spark0"]
        image = replace_color(image, BLACK, fx.color)
      if (x < camera.left
      or y < camera.top
      or x >= camera.right
      or y >= camera.bottom):
        continue
      x += TILE_SIZE // 2 - image.get_width() // 2
      y += TILE_SIZE // 2 - image.get_height() // 2
      sprites.append(Sprite(image=image, pos=(x, y), layer="vfx"))
    return sprites

  def view_numbers(self, numbers, camera):
    sprites = []
    for number in numbers:
      sprites += number.render()
      if number.done:
        numbers.remove(number)
    return sprites

  def view_tiles(self, camera):
    camera = camera.get_rect()
    offset_x, offset_y = self.tile_offset
    dest_x = -camera.left + offset_x * TILE_SIZE
    dest_y = -camera.top + offset_y * TILE_SIZE
    return [Sprite(
      image=self.tile_surface,
      pos=(dest_x, dest_y),
      layer="tiles"
    )]

  def view(self, ctx):
    sprites = []
    visible_cells = ctx.hero.visible_cells
    visited_cells = ctx.get_visited_cells()
    camera = ctx.camera
    anims = ctx.anims
    vfx = ctx.vfx
    numbers = ctx.numbers
    hero = ctx.hero
    stage = ctx.floor
    elems = stage.elems
    decors = stage.decors
    sprites += self.view_decors(decors, camera, visible_cells, visited_cells)
    sprites += self.view_elems(elems, hero, camera, visible_cells, anims)
    sprites += self.view_vfx(vfx, camera)
    sprites += self.view_numbers(numbers, camera)
    for sprite in sprites:
      camera_x, camera_y = camera.pos or (0, 0)
      camera_inv = (-camera_x, -camera_y)
      sprite.move(camera_inv)
    sprites += self.view_tiles(camera)
    sprites.sort(key=StageView.order)
    return sprites

def render_tile(stage, cell, visited_cells=[]):
  assets = use_assets()
  x, y = cell
  sprite_name = None
  tile = stage.get_tile_at(cell)
  tile_above = stage.get_tile_at((x, y - 1))
  tile_below = stage.get_tile_at((x, y + 1))
  tile_base = stage.get_tile_at((x, y + 2))
  tile_nw = stage.get_tile_at((x - 1, y - 1))
  tile_ne = stage.get_tile_at((x + 1, y - 1))
  tile_sw = stage.get_tile_at((x - 1, y + 1))
  tile_se = stage.get_tile_at((x + 1, y + 1))
  if tile is stage.WALL or tile is stage.DOOR_HIDDEN or (
  tile is stage.DOOR_WAY and tile_below is stage.DOOR_HIDDEN):
    room = next((r for r in stage.rooms if cell in r.get_cells() + r.get_border()), None)
    elev = 0
    if room:
      for c in room.get_cells():
        if stage.get_tile_at(c) is stage.FLOOR_ELEV:
          elev = 1
          break
    if ((tile_below is stage.FLOOR or tile_below is stage.PIT or tile_below is stage.FLOOR_ELEV)
    and not isinstance(stage.get_elem_at((x, y + 1)), Door)):
      if x % (3 + y % 2) == 0 or tile is stage.DOOR_HIDDEN:
        sprite_name = "wall_torch"
      else:
        sprite_name = "wall_bottom"
    elif tile_base is stage.FLOOR and elev == 1:
      sprite_name = "wall_top"
    else:
      return render_wall(stage, cell, visited_cells)
  elif tile is stage.FLOOR_ELEV:
    sprite_name = "floor_elev"
  elif tile is stage.WALL_ELEV:
    sprite_name = "wall_elev"
  elif tile is stage.LADDER:
    sprite_name = "ladder"
  elif tile is stage.STAIRS:
    sprite_name = "stairs"
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
  elif tile is stage.OASIS_STAIRS:
    sprite_name = "oasis_stairs"
  elif tile is stage.OASIS:
    return render_oasis(stage, cell)
  elif tile is stage.PUSH_TILE:
    sprite_name = "push_tile"

  if "floor_elev" not in assets.sprites:
    assets.sprites["floor_elev"] = replace_color(assets.sprites["floor"], 0xFF404040, 0xFF7D7D7D)
  if "wall_elev" not in assets.sprites:
    assets.sprites["wall_elev"] = replace_color(assets.sprites["wall_base"], 0xFFFFFFFF, 0xFF7D7D7D)

  return assets.sprites[sprite_name] if sprite_name else None

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
    or isinstance(stage.get_elem_at((x, y)), Door)
  )

  sprite = Surface((TILE_SIZE, TILE_SIZE), SRCALPHA)
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

  if is_wall(x - 1, y) and is_wall(x - 1, y + 1) and (not is_wall(x, y + 2) and not is_door(x, y + 2) or is_door(x, y + 1)):
    sprite.blit(rotate(link, 90), (0, 0))

  if is_wall(x + 1, y) and is_wall(x + 1, y + 1) and (not is_wall(x, y + 2) and not is_door(x, y + 2) or is_door(x, y + 1)):
    sprite.blit(rotate(flip(link, True, False), -90), (0, 0))

  return sprite

def render_oasis(stage, cell):
  sprites = use_assets().sprites
  x, y = cell
  o = lambda x, y: (
    stage.get_tile_at((x, y)) is stage.OASIS
    or stage.get_tile_at((x, y)) is stage.OASIS_STAIRS
  )
  if o(x, y - 1) and o(x, y + 1) and not o(x - 1, y):
    return sprites["oasis_edge"]
  elif o(x, y - 1) and o(x, y + 1) and not o(x + 1, y):
    return flip(sprites["oasis_edge"], True, False)
  if o(x - 1, y) and o(x + 1, y) and not o(x, y - 1):
    return rotate(sprites["oasis_edge"], -90)
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
