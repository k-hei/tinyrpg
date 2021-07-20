from math import ceil
from pygame import Surface, Rect, SRCALPHA
from pygame.transform import rotate, flip, scale
from pygame.time import get_ticks

from assets import load as use_assets
from filters import replace_color, darken_image
from colors import darken_color
from colors.palette import BLACK, WHITE, GRAY, DARKGRAY, COLOR_TILE
from config import ITEM_OFFSET, TILE_SIZE, DEBUG
from sprite import Sprite
from lib.lerp import lerp

from dungeon.actors import DungeonActor
from dungeon.stage import Stage
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

def recolor_walls():
  assets = use_assets()
  for key in assets.sprites.keys():
    if key.startswith("wall") :
      assets.sprites[key] = replace_color(assets.sprites[key], WHITE, COLOR_TILE)

class StageView:
  LAYERS = ["tiles", "decors", "elems", "vfx", "numbers", "ui"]
  SPECIAL_TILES = [Stage.OASIS, Stage.OASIS_STAIRS]
  ELEVATED_TILES = [Stage.FLOOR_ELEV, Stage.WALL_ELEV, Stage.STAIRS_RIGHT]
  VARIABLE_TILES = [
    Stage.FLOOR,
    Stage.WALL,
    Stage.PIT,
    Stage.OASIS,
  ]

  def order(sprite):
    _, sprite_y = sprite.pos
    try:
      depth = StageView.LAYERS.index(sprite.layer)
    except ValueError:
      depth = 0
    depth *= 1000
    y = sprite_y + sprite.offset
    return depth + y

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

  def redraw_tile(self, stage, cell, visited_cells):
    col, row = cell
    offset_x, offset_y = self.tile_offset
    tile = stage.get_tile_at(cell)
    if not tile:
      return False
    tile_name = tile.__name__
    tile_xoffset, tile_yoffset = (0, 0)
    tile_sprite = None
    if tile_name in self.tile_cache and tile not in StageView.VARIABLE_TILES:
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
      and tile is not stage.WALL):
        tile_image = replace_color(tile_image, WHITE, COLOR_TILE)
        tile_image = replace_color(tile_image, GRAY, DARKGRAY)
    x = (col - offset_x) * TILE_SIZE + tile_xoffset
    y = (row - offset_y) * TILE_SIZE + tile_yoffset
    if cell in self.tile_sprites and tile is not self.tile_sprites[cell][0]:
      del self.tile_sprites[cell]
    if tile_sprite is None:
      self.tile_surface.blit(tile_image, (x, y + TILE_SIZE - tile_image.get_height()))
      self.tile_cache[tile_name] = tile_image
      if cell not in self.tile_cache:
        self.tile_cache[cell] = darken_image(tile_image)
    elif cell not in self.tile_sprites:
      x = col * TILE_SIZE
      y = row * TILE_SIZE
      tile_sprite.move((x, y))
      if tile_sprite.origin and tile_sprite.origin[1] == "bottom":
        tile_sprite.move((0, tile_image.get_height()))
      self.tile_sprites[cell] = (tile, tile_sprite)
    return True

  def redraw_tiles(self, stage, camera, visible_cells, visited_cells, force=False):
    time_start = get_ticks()
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
    for row in range(top, bottom + 1):
      for col in range(left, right + 1):
        cell = (col, row)
        if cell in visible_cells:
          self.redraw_tile(stage, cell, visited_cells)
        elif cell in self.tile_cache:
          tile_image = self.tile_cache[cell]
          x = (col - left) * TILE_SIZE
          y = (row - top) * TILE_SIZE
          self.tile_surface.blit(tile_image, (x, y))
    time_end = get_ticks()

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

  def view_elem(self, elem, anims):
    elem.update()
    sprites = elem.view(anims)
    if sprites:
      for sprite in sprites:
        elem_x, elem_y = elem.cell
        sprite.move(((elem_x + 0.5) * TILE_SIZE, (elem_y + 1) * TILE_SIZE))
        move_anim = anims and next((a for a in anims[0] if type(a) is MoveAnim and a.target is elem), None)
        if move_anim:
          _, _, *anim_z = move_anim.cell
          anim_z = anim_z and anim_z[0] or 0
          sprite.offset += anim_z * TILE_SIZE
        else:
          sprite.offset += elem.elev * TILE_SIZE
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
      except:
        raise
    return sprites

  def view_vfx(self, vfx, camera):
    sprites = []
    assets = use_assets()
    camera = camera.get_rect()
    for fx in vfx:
      if fx.done:
        vfx.remove(fx)
        continue
      if "view" in dir(fx):
        vfx += fx.update() or []
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
    sprites += self.view_decors(decors, visible_cells, visited_cells)
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

  if "wall_elev" not in assets.sprites:
    assets.sprites["wall_elev"] = replace_color(flip(assets.sprites["wall_base"], True, False), COLOR_TILE, GRAY)
  if "floor_elev" not in assets.sprites:
    elevfloor_image = Surface((TILE_SIZE, TILE_SIZE * 2), SRCALPHA)
    elevfloor_image.fill(COLOR_TILE)
    elevfloor_image.blit(assets.sprites["floor"], (0, 0))
    elevfloor_image.blit(assets.sprites["wall_elev"], (0, TILE_SIZE))
    assets.sprites["floor_elev"] = elevfloor_image
  if assets.sprites["stairs"].get_height() < TILE_SIZE * 2:
    stairs_image = Surface((TILE_SIZE, TILE_SIZE * 2), SRCALPHA)
    stairs_image.blit(assets.sprites["stairs"], (0, 0))
    stairs_image.blit(assets.sprites["stairs"], (0, TILE_SIZE))
    assets.sprites["stairs"] = stairs_image

  if tile is stage.WALL:
    room = next((r for r in stage.rooms if cell in r.get_cells() + r.get_border()), None)
    elev = 0
    if room:
      for c in room.get_cells():
        if stage.get_tile_at(c) is stage.FLOOR_ELEV:
          elev = 1
          break
    if tile_below is stage.FLOOR_ELEV:
      return Sprite(image=assets.sprites["wall_bottom"], pos=(0, -TILE_SIZE))
    elif ((tile_below is stage.FLOOR or tile_below is stage.PIT)
    and (x, y + 1) in visited_cells
    and not stage.get_elem_at((x, y + 1), superclass=Door)):
      if x % (3 + y % 2) == 0:
        sprite_name = "wall_torch"
      else:
        sprite_name = "wall_bottom"
    elif (tile_base is stage.FLOOR or tile_base is stage.PIT) and elev == 1:
      sprite_name = "wall_top"
    else:
      return render_wall(stage, cell, visited_cells)
  elif tile is stage.FLOOR_ELEV and (
    stage.get_tile_at((x - 1, y)) is stage.FLOOR_ELEV
    and stage.get_tile_at((x + 1, y)) is stage.FLOOR_ELEV
    and stage.get_tile_at((x, y - 1)) is stage.FLOOR_ELEV
    and stage.get_tile_at((x, y + 1)) is stage.FLOOR_ELEV
    and stage.get_tile_at((x - 1, y - 1)) is stage.FLOOR_ELEV
    and stage.get_tile_at((x + 1, y - 1)) is stage.FLOOR_ELEV
    and stage.get_tile_at((x - 1, y + 1)) is stage.FLOOR_ELEV
    and stage.get_tile_at((x + 1, y + 1)) is stage.FLOOR_ELEV):
    return Sprite(image=assets.sprites["floor_fancy"], pos=(0, -TILE_SIZE))
  elif tile is stage.FLOOR_ELEV:
    return Sprite(
      image=assets.sprites["floor_elev"],
      origin=("left", "bottom"),
      layer="elems",
      offset=-TILE_SIZE,
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
      offset=-TILE_SIZE,
    )
  elif tile is stage.STAIRS_UP:
    sprite_name = "stairs_up"
  elif tile is stage.STAIRS_DOWN:
    sprite_name = "stairs_down"
  elif tile is stage.STAIRS_RIGHT:
    return Sprite(
      image=flip(assets.sprites["stairs_right"], True, False),
      origin=("left", "bottom"),
      layer="elems",
      offset=-TILE_SIZE,
    )
  elif tile is stage.FLOOR and (
    stage.get_tile_at((x - 1, y)) is stage.FLOOR
    and stage.get_tile_at((x + 1, y)) is stage.FLOOR
    and stage.get_tile_at((x, y - 1)) is stage.FLOOR
    and stage.get_tile_at((x, y + 1)) is stage.FLOOR
    and stage.get_tile_at((x - 1, y - 1)) is stage.FLOOR
    and stage.get_tile_at((x + 1, y - 1)) is stage.FLOOR
    and stage.get_tile_at((x - 1, y + 1)) is stage.FLOOR
    and stage.get_tile_at((x + 1, y + 1)) is stage.FLOOR
  ):
    sprite_name = "floor_fancy"
  elif tile is stage.FLOOR:
    if next((e for e in stage.elems if e.cell[1] < y), None) and (
      stage.get_tile_at((x, y - 1)) is stage.PIT
      or stage.get_tile_at((x, y - 2)) is stage.PIT
    ):
      return Sprite(
        image=replace_color(assets.sprites["floor"], GRAY, DARKGRAY),
        layer="elems",
      )
    sprite_name = "floor"
  elif tile is stage.PIT:
    if tile_above and tile_above is not stage.PIT:
      sprite_name = "pit"
    else:
      return None
  elif tile is stage.OASIS_STAIRS:
    sprite_name = "oasis_stairs"
  elif tile is stage.OASIS:
    return render_oasis(stage, cell)

  return assets.sprites[sprite_name] if sprite_name else None

def render_wall(stage, cell, visited_cells=[]):
  assets = use_assets()
  x, y = cell
  def is_wall(x, y):
    door = stage.get_elem_at((x, y), superclass=Door)
    return (
      (x, y) not in visited_cells
      or stage.get_tile_at((x, y)) is None
      or stage.get_tile_at((x, y)) is stage.WALL and (
        (x, y + 1) not in visited_cells
        or stage.get_tile_at((x, y + 1)) is None
        or stage.get_tile_at((x, y + 1)) is stage.WALL
        or stage.get_elem_at((x, y + 1), superclass=Door))
    )
  is_door = lambda x, y: stage.get_elem_at((x, y), superclass=Door)

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

  if not is_wall(x - 1, y):
    sprite.blit(edge_left, (0, 0))
    if is_wall(x, y - 1):
      sprite.blit(link, (0, 0))
    if is_wall(x, y + 1):
      sprite.blit(flip(link, False, True), (0, 0))

  if not is_wall(x + 1, y):
    sprite.blit(edge_right, (0, 0))
    if is_wall(x, y - 1):
      sprite.blit(flip(link, True, False), (0, 0))
    if is_wall(x, y + 1):
      sprite.blit(flip(link, True, True), (0, 0))

  if not is_wall(x, y - 1):
    sprite.blit(edge_top, (0, 0))

  if not is_wall(x, y + 1):
    sprite.blit(edge_bottom, (0, 0))

  if (is_wall(x - 1, y) and is_wall(x, y - 1) and not is_wall(x - 1, y - 1)
  or not is_wall(x - 1, y) and not is_wall(x, y - 1)):
    sprite.blit(corner_nw, (0, 0))

  if (is_wall(x + 1, y) and is_wall(x, y - 1) and not is_wall(x + 1, y - 1)
  or not is_wall(x + 1, y) and not is_wall(x, y - 1)):
    sprite.blit(corner_ne, (0, 0))

  if (is_wall(x - 1, y) and is_wall(x, y + 1) and not is_wall(x - 1, y + 1)
  or not is_wall(x - 1, y) and not is_wall(x, y + 1)):
    sprite.blit(corner_sw, (0, 0))

  if (is_wall(x + 1, y) and is_wall(x, y + 1) and not is_wall(x + 1, y + 1)
  or not is_wall(x + 1, y) and not is_wall(x, y + 1)):
    sprite.blit(corner_se, (0, 0))

  if not is_wall(x, y - 1) and is_wall(x - 1, y):
    sprite.blit(rotate(flip(link, False, True), -90), (0, 0))

  if not is_wall(x, y - 1) and is_wall(x + 1, y):
    sprite.blit(rotate(link, -90), (0, 0))

  if is_wall(x - 1, y) and not is_wall(x, y + 1):
    sprite.blit(rotate(link, 90), (0, 0))

  if is_wall(x + 1, y) and not is_wall(x, y + 1):
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
  elif o(x - 1, y) and o(x + 1, y) and not o(x, y - 1):
    return sprites["oasis_edge_top"]
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
