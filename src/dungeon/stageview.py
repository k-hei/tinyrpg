from math import inf, ceil
from pygame import Surface, Rect, SRCALPHA
from pygame.transform import rotate, flip, scale
from pygame.time import get_ticks

from lib.lerp import lerp
from lib.cell import add as add_vector, neighborhood
import debug
import assets
from assets import load as use_assets
from lib.filters import replace_color, darken_image
from colors import darken_color
from colors.palette import BLACK, WHITE, GRAY, DARKGRAY, COLOR_TILE
from config import ITEM_OFFSET, TILE_SIZE, DEBUG, WINDOW_HEIGHT, DEPTH_SIZE
from lib.sprite import Sprite

from dungeon.actors import DungeonActor
from dungeon.stage import Stage
from dungeon.props.chest import Chest
from dungeon.props.soul import Soul
from dungeon.props.palm import Palm
from dungeon.props.door import Door
from dungeon.props.pushtile import PushTile
from dungeon.props.trap import Trap
from dungeon.props.secretdoor import SecretDoor
from dungeon.render.walltop import render_walltop

from anims import Anim
from anims.step import StepAnim
from anims.jump import JumpAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.bounce import BounceAnim
from anims.pause import PauseAnim
from anims.awaken import AwakenAnim
from anims.item import ItemAnim
from anims.tween import TweenAnim
from anims.shake import ShakeAnim

def recolor_walls():
  assets = use_assets()
  for key in assets.sprites.keys():
    if key.startswith("wall"):
      assets.sprites[key] = replace_color(assets.sprites[key], WHITE, COLOR_TILE)

def get_tile_visited_state(stage, cell, visited_cells):
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
    SecretDoor.exists_at(stage, (x - 1, y)),
    SecretDoor.exists_at(stage, (x + 1, y)),
    SecretDoor.exists_at(stage, (x, y - 1)),
    SecretDoor.exists_at(stage, (x, y + 1)),
  ]

class StageView:
  LAYERS = ["tiles", "decors", "elems", "vfx", "numbers", "ui"]
  SPECIAL_TILES = [] # Tiles that appear white (subject to change)
  ELEVATED_TILES = [Stage.FLOOR_ELEV, Stage.WALL_ELEV, Stage.STAIRS, Stage.STAIRS_LEFT, Stage.STAIRS_RIGHT]
  VARIABLE_TILES = [Stage.WALL, Stage.FLOOR, Stage.OASIS, Stage.PIT, Stage.HALLWAY] # Tiles with more than one possible image (generic cache override)

  class FadeAnim(TweenAnim): pass
  class DarkenAnim(Anim): pass

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

  def __init__(self, size):
    width, height = size
    width += TILE_SIZE * 2
    height += TILE_SIZE * 2
    self.tile_surface = Surface((width, height), SRCALPHA)
    self.tile_offset = (0, 0)
    self.tile_cache = {}
    self.tile_sprites = {}
    self.camera_cell = None
    self.stage = None
    self.facings = {}
    self.anim = None
    self.darkened = False

  def redraw_tile(self, stage, cell, visible_cells, visited_cells, anims=[], dry=False):
    tile_col, tile_row = cell

    tile = stage.get_tile_at(cell)
    if not tile:
      return False

    tile_visited_state = get_tile_visited_state(stage, cell, visited_cells)
    if cell in self.tile_cache and tile_visited_state != self.tile_cache[cell][0]:
      del self.tile_cache[cell]
    if cell in self.tile_sprites and tile is not self.tile_sprites[cell][0]:
      del self.tile_sprites[cell]

    tile_name = tile.__name__
    tile_xoffset, tile_yoffset = (0, 0)
    tile_sprite = None

    if cell in self.tile_cache:
      tile_image = self.tile_cache[cell][1]
    elif tile_name in self.tile_cache and tile not in StageView.VARIABLE_TILES:
      tile_image = self.tile_cache[tile_name]
    else:
      tile_image = render_tile(stage, cell, visited_cells)
      if type(tile_image) is Sprite:
        tile_sprite = tile_image
        tile_image = tile_sprite.image
        tile_xoffset, tile_yoffset = tile_sprite.pos
      if not tile_image:
        return False
      if (tile not in StageView.SPECIAL_TILES
      and tile not in StageView.ELEVATED_TILES
      and tile is not stage.WALL
      and tile is not stage.FLOOR
      ):
        tile_image = replace_color(tile_image, WHITE, COLOR_TILE)
        tile_image = replace_color(tile_image, GRAY, DARKGRAY)

    if tile_sprite is None:
      if cell not in self.tile_cache:
        self.tile_cache[cell] = (tile_visited_state, tile_image, darken_image(tile_image))
      if tile_name not in self.tile_cache:
        self.tile_cache[tile_name] = tile_image
    elif cell not in self.tile_cache and tile_sprite.image.get_height() == TILE_SIZE:
      self.tile_cache[cell] = (tile_visited_state, tile_sprite.image, darken_image(tile_sprite.image))

    offset_col, offset_row = self.tile_offset
    tile_x = (tile_col - offset_col) * TILE_SIZE + tile_xoffset
    tile_y = (tile_row - offset_row) * TILE_SIZE + tile_yoffset
    if tile_sprite and cell not in self.tile_sprites:
      tile_x = tile_col * TILE_SIZE
      tile_y = tile_row * TILE_SIZE
      tile_sprite.move((tile_x, tile_y))
      if tile_sprite.origin and tile_sprite.origin[1] == "bottom":
        tile_sprite.move((0, TILE_SIZE))
        tile_sprite.offset = tile_sprite.offset or -1
      self.tile_sprites[cell] = (tile, tile_sprite)

    if dry:
      return True

    # fade animation
    fade_anim = None
    for group in anims:
      fade_anim = next((a for a in group if type(a) is StageView.FadeAnim), None)
      if fade_anim:
        break
    if fade_anim:
      anim_cells = fade_anim.target if not fade_anim.done else []
      if cell in anim_cells:
        if fade_anim.time:
          tile_image = darken_image(tile_image) if tile_sprite else self.tile_cache[cell][2]
        else:
          tile_image = None

    if tile_image and not tile_sprite:
      self.tile_surface.blit(tile_image, (tile_x, tile_y + TILE_SIZE - tile_image.get_height()))

    if tile_sprite:
      if tile_image:
        tile_sprite.image = tile_image
      else:
        del self.tile_sprites[cell]

    return True

  def redraw_tiles(self, stage, camera, visible_cells, visited_cells, anims=[], force=False):
    sprites = []
    camera_x, camera_y = camera.cell
    camera_cell = (int(camera_x), int(camera_y))
    if camera_cell == self.camera_cell and not force:
      return
    camera_rect = camera.get_rect()
    camera_oldrect = camera.get_rect(camera.cell)
    snap = lambda rect: (
      rect.left // TILE_SIZE - 1,
      rect.top // TILE_SIZE - 1,
      ceil(rect.right / TILE_SIZE) + 1,
      ceil(rect.bottom / TILE_SIZE) + 1
    )
    old_left, old_top, old_right, old_bottom = snap(camera_oldrect)
    new_left, new_top, new_right, new_bottom = snap(camera_rect)
    left = min(old_left, new_left)
    top = min(old_top, new_top)
    right = max(old_right, new_right)
    bottom = max(old_bottom, new_bottom)
    cols = right - left + 1
    rows = bottom - top + 1
    self.tile_surface = Surface((cols * TILE_SIZE, rows * TILE_SIZE), SRCALPHA)
    self.tile_offset = (left, top)
    self.tile_sprites = {}
    self.camera_cell = camera_cell
    if stage is not self.stage:
      self.stage = stage
      self.tile_cache = {}
      recolor_walls()

    darken_anim = self.darkened # next((a for g in anims for a in g if type(a) is StageView.DarkenAnim), None)
    fade_anim = next((a for g in anims for a in g if type(a) is StageView.FadeAnim), None)
    anim_cells = fade_anim.target.copy() if fade_anim else []

    for row in range(top, bottom + 1):
      for col in range(left, right + 1):
        cell = (col, row)
        if cell in visible_cells + anim_cells and not darken_anim:
          self.redraw_tile(stage, cell, visible_cells, visited_cells, anims)
          if cell in anim_cells:
            anim_cells.remove(cell)
        elif cell in self.tile_cache:
          _, _, tile_image = self.tile_cache[cell]
          x = (col - left) * TILE_SIZE
          y = (row - top) * TILE_SIZE
          self.tile_surface.blit(tile_image, (x, y))

    for cell in anim_cells:
      self.redraw_tile(stage, cell, visible_cells, visited_cells, anims, dry=True)

  def view_tiles(self, camera):
    camera = camera.get_rect()
    offset_x, offset_y = self.tile_offset
    dest_x = -camera.left + offset_x * TILE_SIZE
    dest_y = -camera.top + offset_y * TILE_SIZE
    tile_sprites = [s.copy() for t, s in self.tile_sprites.values()]
    for sprite in tile_sprites:
      sprite.move((-camera.left, -camera.top))
    return [Sprite(
      image=self.tile_surface,
      pos=(dest_x, dest_y),
      layer="tiles"
    ), *tile_sprites]

  def view_decors(self, decors, visible_cells, visited_cells):
    sprites = []
    for decor in decors:
      if decor.cell not in visited_cells:
        continue
      decor_sprite = decor.view()[0]
      if decor.cell not in visible_cells:
        decor_sprite.image = darken_image(decor_sprite.image)
      sprites.append(decor_sprite)
    return sprites

  def view_elem(self, elem, stage, visited_cells, anims):
    if type(elem) is SecretDoor and elem.hidden:
      return [Sprite(
        image=render_wall(stage, elem.cell, visited_cells),
        pos=tuple([x * TILE_SIZE for x in elem.cell]),
        layer="tiles"
      )]
    sprites = elem.view(anims)
    if sprites:
      for sprite in sprites:
        elem_x, elem_y = elem.cell
        sprite.move(((elem_x + 0.5) * TILE_SIZE, (elem_y + 1) * TILE_SIZE))
        move_anim = anims and next((a for a in anims[0] if type(a) is StepAnim and a.target is elem), None)
        if move_anim and move_anim.cell:
          _, _, *anim_z = move_anim.cell
          anim_z = anim_z and anim_z[0] or 0
          sprite.offset += anim_z * TILE_SIZE
        else:
          sprite.offset += elem.elev * TILE_SIZE
        sprite.origin = ("center", "bottom")
        if self.darkened and elem.static and not elem.active:
          sprite.image = darken_image(sprite.image)
      return sprites
    else:
      return []

  def view_elems(self, elems, stage, hero, camera, visible_cells, visited_cells, anims):
    time_start = get_ticks()
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
      elem_anims = [a for g in anims for a in g if a.target is elem] if anims else []
      if (
        x + TILE_SIZE < camera.left
        or y + TILE_SIZE < camera.top
        or x > camera.right
        or y > camera.bottom
      ) and not elem_anims:
        return False
      return True
    visible_elems = [e for e in elems if is_visible(e)]
    for elem in visible_elems:
      try:
        sprites += self.view_elem(elem, stage, visited_cells, anims)
      except:
        raise
    time_end = get_ticks()
    # debug.log("Redraw dungeon elements in {}ms".format(time_end - time_start))
    return sprites

  def view_vfx(self, vfx, camera):
    sprites = []
    assets = use_assets()
    camera = camera.get_rect()
    for fx in vfx:
      if "view" in dir(fx):
        sprites += fx.view()
        continue
      elif fx.kind:
        frame = fx.update()
        if frame == None:
          continue
        image = assets.sprites[frame]
        if fx.color:
          image = replace_color(image, BLACK, fx.color)
      else:
        fx.update()
        image = assets.sprites["fx_spark0"]
        image = replace_color(image, BLACK, fx.color)
      x, y = fx.pos
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

  def shake(self, duration=15, vertical=False):
    self.anim = ShakeAnim(duration=duration, target=vertical)

  def stop_shake(self):
    self.anim = None

  def update(self):
    if self.anim:
      if self.anim.done:
        self.anim = None
      else:
        self.anim.update()

  def view(self, ctx):
    time_start = get_ticks()
    self.update()
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
    sprites += self.view_decors(decors, visible_cells, visited_cells)
    sprites += self.view_elems(elems, stage, hero, camera, visible_cells, visited_cells, anims)
    sprites += self.view_vfx(vfx, camera)
    sprites += self.view_numbers(numbers, camera)
    camera_offset = None
    for sprite in sprites:
      camera_x, camera_y = camera.pos or (0, 0)
      camera_offset = (0, 0)
      if self.anim:
        if self.anim.target:
          camera_offset = (0, self.anim.offset)
        else:
          camera_offset = (self.anim.offset, 0)
      camera_pos = (-int(camera_x), -int(camera_y))
      if sprite.layer != "ui":
        sprite.move(camera_pos)
    sprites += self.view_tiles(camera)
    for sprite in sprites:
      if sprite.layer != "ui" and camera_offset:
        sprite.move(camera_offset)
    sprites.sort(key=StageView.order)
    time_end = get_ticks()
    # debug.log("Redraw stage in {}ms".format(time_end - time_start))
    return sprites

def render_tile(stage, cell, visited_cells=[]):
  sprite_name = None
  x, y = cell
  tile = stage.get_tile_at(cell)
  tile_above = stage.get_tile_at((x, y - 1))
  tile_below = stage.get_tile_at((x, y + 1))
  tile_base = stage.get_tile_at((x, y + 2))
  tile_nw = stage.get_tile_at((x - 1, y - 1))
  tile_ne = stage.get_tile_at((x + 1, y - 1))
  tile_sw = stage.get_tile_at((x - 1, y + 1))
  tile_se = stage.get_tile_at((x + 1, y + 1))

  if "wall_elev" not in assets.sprites:
    assets.sprites["wall_elev"] = replace_color(flip(assets.sprites["wall_base"], True, False), COLOR_TILE, GRAY)
  if "floor_elev" not in assets.sprites:
    elevfloor_image = Surface((TILE_SIZE, TILE_SIZE * 2), SRCALPHA)
    elevfloor_image.fill(COLOR_TILE)
    elevfloor_image.blit(assets.sprites["floor"], (0, 0))
    elevfloor_image.blit(assets.sprites["wall_elev"], (0, TILE_SIZE))
    elevfloor_image = replace_color(elevfloor_image, DARKGRAY, GRAY)
    assets.sprites["floor_elev"] = elevfloor_image
  if "floor_fancy_elev" not in assets.sprites:
    elevfloor_image = replace_color(assets.sprites["floor_fancy"], DARKGRAY, GRAY)
    assets.sprites["floor_fancy_elev"] = elevfloor_image
  if "stairs_right" not in assets.sprites:
    assets.sprites["stairs_right"] = flip(assets.sprites["stairs_left"], True, False)
  if assets.sprites["stairs"].get_height() < TILE_SIZE * 2:
    stairs_template = replace_color(assets.sprites["stairs"], DARKGRAY, GRAY)
    stairs_image = Surface((TILE_SIZE, TILE_SIZE * 2), SRCALPHA)
    stairs_image.blit(stairs_template, (0, 0))
    stairs_image.blit(stairs_template, (0, TILE_SIZE))
    assets.sprites["stairs"] = stairs_image

  if tile is stage.WALL:
    return render_wall(stage, cell, visited_cells)
  elif tile is stage.HALLWAY:
    if SecretDoor.exists_at(stage, (x, y + 1)):
      return render_wall(stage, cell, visited_cells)
    else:
      return None
  elif tile is stage.FLOOR_ELEV:
    return Sprite(
      image=assets.sprites["floor_elev"],
      origin=("left", "bottom"),
      layer="elems",
      offset=-TILE_SIZE // 2 + 1
    )
  elif tile is stage.WALL_ELEV:
    sprite_name = "wall_elev"
  elif tile is stage.LADDER:
    sprite_name = "ladder"
  elif tile is stage.STAIRS:
    return Sprite(
      image=assets.sprites["stairs"],
      origin=("left", "bottom"),
      layer="elems",
      offset=-TILE_SIZE
    )
  elif tile is stage.STAIRS_UP:
    sprite_name = "stairs_up"
  elif tile is stage.STAIRS_DOWN:
    sprite_name = "stairs_down"
  elif tile is stage.STAIRS_EXIT:
    sprite_name = "stairs_up"
  elif tile is stage.STAIRS_LEFT:
    return Sprite(
      image=assets.sprites["stairs_left"],
      origin=("left", "bottom"),
      layer="elems",
      offset=-TILE_SIZE
    )
  elif tile is stage.STAIRS_RIGHT:
    return Sprite(
      image=assets.sprites["stairs_right"],
      origin=("left", "bottom"),
      layer="elems",
      offset=-TILE_SIZE
    )
  elif tile is stage.FLOOR and (
    next((n for n in neighborhood(cell) for e in stage.get_elems_at(n) if isinstance(e, Door) and not isinstance(e, SecretDoor)), None)
  ):
    sprite_name = "floor_fancy"
  elif tile is stage.FLOOR:
    if (next((e for e in stage.elems if e.cell[1] < y), None)
    and stage.get_tile_at((x, y - 1)) is stage.PIT):
      return Sprite(
        image=replace_color(assets.sprites["floor"], GRAY, DARKGRAY),
        layer="elems",
      )
    elif next((e for e in stage.get_elems_at(cell) if type(e) is PushTile or isinstance(e, Trap)), None):
      return None
    else:
      sprite_name = "floor"
  elif tile is stage.PIT:
    if tile_above and tile_above is not stage.PIT:
      sprite_name = "pit"
    else:
      return None
  elif tile is stage.OASIS_STAIRS:
    if stage.get_tile_at((x, y - 1)) is stage.FLOOR:
      sprite_name = "oasis_stairs_down"
    else:
      sprite_name = "oasis_stairs_up"
  elif tile is stage.OASIS:
    return render_oasis(stage, cell)
  return assets.sprites[sprite_name] if sprite_name else None

def render_wall(stage, cell, visited_cells=None):
  x, y = cell
  tile_below = stage.get_tile_at((x, y + 1))
  tile_base = stage.get_tile_at((x, y + 2))
  room = next((r for r in stage.rooms if cell in r.get_cells() + r.get_outline()), None)
  is_elevated = room and next((c for c in room.get_cells() if stage.get_tile_at(c) is stage.FLOOR_ELEV), False)
  is_special_room = not is_elevated and room and room.data and room.data.tiles

  if tile_below is stage.FLOOR_ELEV:
    return Sprite(image=assets.sprites["wall_bottom"], pos=(0, -TILE_SIZE))
  elif ((
    tile_below is stage.FLOOR
    or tile_below is stage.PIT
    or tile_below is stage.HALLWAY
    or tile_below is stage.OASIS
  )
  and (visited_cells is None or (x, y + 1) in visited_cells)
  and not stage.get_elem_at((x, y + 1), superclass=Door)):
    if is_special_room:
      if x % (2 + y % 2) == 0 or SecretDoor.exists_at(stage, cell):
        return assets.sprites["wall_battle_alt"]
      else:
        return assets.sprites["wall_battle"]
    else:
      if x % (3 + y % 2) == 0 or SecretDoor.exists_at(stage, cell):
        return assets.sprites["wall_alt"]
      else:
        return assets.sprites["wall_bottom"]
  elif is_elevated and tile_below is stage.WALL and not (tile_base is None or tile_base is stage.WALL):
    return assets.sprites["wall_top"]
  else:
    return render_walltop(stage, cell, visited_cells)

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
  elif o(x - 1, y) and o(x + 1, y) and not o(x, y - 1):
    return sprites["oasis_edge_top"]
  elif o(x - 1, y) and o(x + 1, y) and not o(x, y + 1):
    return sprites["oasis_edge_bottom"]
  elif o(x + 1, y) and o(x, y + 1) and not o(x - 1, y - 1) and not o(x - 1, y) and not o(x, y - 1):
    return sprites["oasis_corner_top"]
  elif o(x - 1, y) and o(x, y + 1) and not o(x + 1, y - 1) and not o(x + 1, y) and not o(x, y - 1):
    return flip(sprites["oasis_corner_top"], True, False)
  elif o(x + 1, y) and o(x, y - 1) and not o(x - 1, y + 1) and not o(x - 1, y) and not o(x, y + 1):
    return sprites["oasis_corner_bottom"]
  elif o(x - 1, y) and o(x, y - 1) and not o(x + 1, y + 1) and not o(x + 1, y) and not o(x, y + 1):
    return flip(sprites["oasis_corner_bottom"], True, False)
