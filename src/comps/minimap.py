from math import ceil
import pygame
from pygame import Surface, Rect, PixelArray, SRCALPHA
from pygame.transform import scale
from dungeon.stage import Stage
from dungeon.actors.knight import Knight
from dungeon.actors import DungeonActor
from dungeon.actors.mage import Mage
from dungeon.actors.mimic import Mimic
from dungeon.actors.npc import Npc
from dungeon.props.chest import Chest
from dungeon.props.rarechest import RareChest
from dungeon.props.coffin import Coffin
from dungeon.props.vase import Vase
from dungeon.props.itemdrop import ItemDrop
from dungeon.props.soul import Soul
from dungeon.props.door import Door
from dungeon.props.secretdoor import SecretDoor
from dungeon.props.pillar import Pillar
from dungeon.props.table import Table
from dungeon.props.altar import Altar
from colors.palette import GREEN, DARKGREEN, VIOLET, DARKVIOLET
from anims.tween import TweenAnim
from anims.warpin import WarpInAnim
from easing.expo import ease_out, ease_in_out
from lib.lerp import lerp
from lib.bounds import find_bounds
from lib.cell import subtract as subtract_vector
from lib.sprite import Sprite
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_SIZE, DEBUG_GEN

MARGIN_X = 8
MARGIN_Y = 6
ENTER_DURATION = 8
EXIT_DURATION = 4
EXPAND_DURATION = 15
SHRINK_DURATION = 10
BLACKOUT_DURATION = 10
BLACKOUT_DELAY = 60
BLACKOUT_FRAMES = 3
COLOR_KEY = (255, 0, 255)
COLOR_WALL = 0x00CCFF

class EnterAnim(TweenAnim):
  def __init__(anim):
    super().__init__(duration=ENTER_DURATION)
class ExitAnim(TweenAnim):
  def __init__(anim):
    super().__init__(duration=EXIT_DURATION)
class ExpandAnim(TweenAnim):
  def __init__(anim):
    super().__init__(duration=EXPAND_DURATION)
class ShrinkAnim(TweenAnim):
  def __init__(anim):
    super().__init__(duration=SHRINK_DURATION)

class Minimap:
  SIZE_INIT = (16, 16)
  SCALE_INIT = 3
  SCALE_EXPAND = 5
  BLACKOUT_DELAY = 120

  def render_surface(floor, size=None, focus=None, visible_cells=None, visited_cells=None, anims=[], blink=False):
    floor_width, floor_height = floor.size
    filled = not visible_cells and not visited_cells
    visible_cells = visible_cells or floor.get_cells()
    visited_cells = visited_cells or visible_cells
    bounds = filled and Rect((0, 0), floor.size) or find_bounds(visited_cells)
    sprite_size = tuple(map(ceil, size or bounds.size))
    sprite_width, sprite_height = sprite_size

    surface = Surface(sprite_size)
    surface.fill(COLOR_WALL if filled else COLOR_KEY)
    surface.set_colorkey(COLOR_KEY)
    pixels = PixelArray(surface)

    for cell in visited_cells:
      col, row = cell
      if col < 0 or row < 0 or col >= floor_width or row >= floor_height:
        continue

      tile = floor.get_tile_at(cell)
      tile_above = floor.get_tile_at((col, row - 1))
      tile_below = floor.get_tile_at((col, row + 1))

      if focus:
        focus_x, focus_y = focus
        x = int(col - focus_x + sprite_width / 2)
        y = int(row - focus_y + sprite_height / 2)
        if x < 0 or y < 0 or x >= sprite_width or y >= sprite_height:
          continue
      else:
        x, y = col, row

      elem = next((e for e in floor.get_elems_at(cell)), None)
      if next((g for g in anims if next((a for a in g if type(a) is WarpInAnim and a.target is elem), None)), None):
        elem = None

      # f(floor, cell, visible_cells=None, blink=False) -> color
      color = None
      if isinstance(elem, DungeonActor) and elem.faction == "player" and cell in visible_cells:
        color = (0x3399FF, 0x0066CC)[blink]
      elif isinstance(elem, DungeonActor) and elem.faction == "ally" and cell in visible_cells:
        color = (0x33FF99, 0x00CC66)[blink]
      elif type(elem) is Mimic and cell in visible_cells:
        if elem.idle:
          color = (0xFFFF00, 0x7F7F00)[blink]
        else:
          color = (0xFF0000, 0x990000)[blink]
      elif isinstance(elem, DungeonActor) and elem.faction == "enemy" and cell in visible_cells:
        if elem.ailment == "sleep":
          color = 0x990000
        elif elem.aggro:
          color = 0xFF0000
        else:
          color = (0xFF0000, 0x990000)[blink]
      elif isinstance(elem, Soul) and cell in visible_cells:
        color = (VIOLET, DARKVIOLET)[blink]
      elif isinstance(elem, Npc) and cell in visible_cells:
        color = (GREEN, DARKGREEN)[blink]
      elif isinstance(elem, Chest) and elem.rare:
        if elem.opened:
          color = 0x7F007F
        else:
          color = (0xFF00FF, 0x7F007F)[blink]
      elif type(elem) in (Chest, RareChest, Coffin, Vase):
        if elem.opened:
          color = 0x7F7F00
        else:
          color = (0xFFFF00, 0x7F7F00)[blink]
      elif type(elem) is ItemDrop:
        color = (0xFFFF00, 0x7F7F00)[blink]
      elif type(elem) is Altar:
        color = (0xFFFF00, 0x7F7F00)[blink]
      elif (tile is Stage.WALL
      or isinstance(elem, Door) and elem.locked
      or type(elem) is SecretDoor and elem.hidden
      or tile is Stage.HALLWAY and SecretDoor.exists_at(floor, (col, row + 1))
      or type(elem) is Pillar
      or type(elem) is Table and Rect(elem.cell, elem.size).collidepoint(cell)
      ):
        if cell in visible_cells:
          if filled:
            continue
          color = COLOR_WALL
        else:
          color = 0x0066CC
      elif isinstance(elem, Door) and not elem.opened:
        if cell in visible_cells:
          color = 0x0066CC
        else:
          color = 0x0033CC
      elif isinstance(elem, Door) and elem.opened:
        if cell in visible_cells:
          color = 0x003399
        else:
          color = 0x003399
      elif tile is Stage.STAIRS_UP:
        color = (0x00FF00, 0x007F00)[blink]
      elif tile is Stage.STAIRS_DOWN:
        color = 0x007F00
      elif tile is Stage.PIT:
        if cell in visible_cells:
          color = 0x000033
      elif tile is Stage.OASIS or tile is Stage.OASIS_STAIRS:
        if cell in visible_cells:
          color = 0x007F00
        else:
          color = 0x003300
      elif tile is Stage.FLOOR_ELEV or tile is Stage.WALL_ELEV or tile is Stage.STAIRS:
        if cell in visible_cells:
          color = 0x0066CC
        else:
          color = 0x0033CC
      else:
        if cell in visible_cells:
          color = 0x003399
        else:
          color = 0x000066

      if color is not None:
        try:
          pixels[x, y] = color
        except IndexError:
          print((x, y), sprite_size)
          raise

    pixels.close()
    return surface

  def __init__(minimap, parent):
    minimap.parent = parent
    minimap.focus = None
    minimap.time = 0
    minimap.active = False
    minimap.expanded = 0
    minimap.sprite = None
    minimap.anims = []
    minimap.enter()

  def enter(minimap):
    minimap.active = True
    minimap.anims.append(EnterAnim())

  def exit(minimap):
    minimap.active = False
    minimap.anims.append(ExitAnim())

  def expand(minimap):
    minimap.expanded = 1
    minimap.anims.append(ExpandAnim())

  def shrink(minimap):
    minimap.expanded = 0
    minimap.anims.append(ShrinkAnim())

  def is_focused(minimap):
    return minimap.expanded >= BLACKOUT_DELAY + BLACKOUT_FRAMES

  def render(minimap, t=None):
    if t is None:
      t = 1 if minimap.expanded else 0

    # requires: game.hero, game.floor, game.memory?
    # updates whenever any of the following occur:
    # - data changes
    # - visited cells change
    # - camera position (hero cell) changes

    game = minimap.parent
    floor = game.floor
    hero = game.hero
    if not hero or not hero.cell:
      return minimap.sprite

    visible_cells = game.hero.visible_cells
    visited_cells = game.get_visited_cells()

    bounds = find_bounds(visited_cells) if t else Rect((0, 0), floor.size)
    start_width, start_height = Minimap.SIZE_INIT
    end_width, end_height = bounds.size
    start_scale, end_scale = Minimap.SCALE_INIT, Minimap.SCALE_EXPAND
    while end_height * end_scale > WINDOW_HEIGHT * 3 / 4:
      end_scale -= 1

    sprite_width = lerp(start_width, end_width, t)
    sprite_height = lerp(start_height, end_height, t)
    sprite_scale = lerp(start_scale, end_scale, t)

    start_xoffset, start_yoffset = (0, 0)
    end_xoffset, end_yoffset = subtract_vector((0, 0), bounds.topleft)
    start_x, start_y = hero.cell
    end_x, end_y = sprite_width // 2, sprite_height // 2
    focus_x = round(lerp(start_x, end_x, t) - lerp(start_xoffset, end_xoffset, t))
    focus_y = round(lerp(start_y, end_y, t) - lerp(start_yoffset, end_yoffset, t))

    minimap_image = Minimap.render_surface(
      floor=floor,
      size=(sprite_width, sprite_height),
      focus=(focus_x, focus_y),
      visible_cells=visible_cells,
      visited_cells=visited_cells,
      anims=game.anims,
      blink=minimap.time % 60 >= 30
    )

    scaled_width = round(sprite_width * sprite_scale)
    scaled_height = round(sprite_height * sprite_scale)
    scaled_size = (scaled_width, scaled_height)

    surface = Surface(scaled_size)
    surface.fill(COLOR_KEY)
    surface.set_colorkey(COLOR_KEY)
    surface.blit(scale(minimap_image, scaled_size), (0, 0))
    return surface

  def view(minimap):
    sprites = []
    minimap.time += 1

    if minimap.sprite is None:
      minimap.sprite = minimap.render()
      redrawn = True
    else:
      redrawn = False

    corner_x = WINDOW_WIDTH - minimap.sprite.get_width() - MARGIN_X
    corner_y = MARGIN_Y
    center_x = WINDOW_WIDTH // 2 - minimap.sprite.get_width() // 2
    center_y = WINDOW_HEIGHT // 2 - minimap.sprite.get_height() // 2
    anim = minimap.anims[0] if minimap.anims else None
    if anim:
      t = anim.update()
      if type(anim) is EnterAnim:
        t = ease_out(t)
        start_x, start_y = WINDOW_WIDTH, corner_y
        target_x, target_y = corner_x, corner_y
      elif type(anim) is ExitAnim:
        start_x, start_y = corner_x, corner_y
        target_x, target_y = WINDOW_WIDTH, corner_y

      if type(anim) in (ExpandAnim, ShrinkAnim):
        t = ease_in_out(t)
        redrawn = True
        if type(anim) is ExpandAnim:
          minimap.sprite = minimap.render(t)
        elif type(anim) is ShrinkAnim:
          minimap.sprite = minimap.render(1 - t)
        center_x = WINDOW_WIDTH // 2 - minimap.sprite.get_width() // 2
        center_y = WINDOW_HEIGHT // 2 - minimap.sprite.get_height() // 2

      if type(anim) is ExpandAnim:
        start_x, start_y = corner_x, corner_y
        target_x, target_y = center_x, center_y
      elif type(anim) is ShrinkAnim:
        start_x, start_y = center_x, center_y
        target_x, target_y = corner_x, corner_y

      x = lerp(start_x, target_x, t)
      y = lerp(start_y, target_y, t)
      if anim.done:
        minimap.anims.pop(0)
    elif minimap.expanded:
      x = center_x
      y = center_y
      minimap.expanded += 1
      if minimap.is_focused():
        t = min(1, (minimap.expanded - BLACKOUT_DELAY) / BLACKOUT_DURATION)
        alpha = min(0xFF, int(t * BLACKOUT_FRAMES) / BLACKOUT_FRAMES * 0xFF)
        fill = Surface(WINDOW_SIZE, pygame.SRCALPHA)
        pygame.draw.rect(fill, (0, 0, 0, alpha), fill.get_rect())
        sprites.append(Sprite(
          image=fill,
          pos=(0, 0),
          layer="hud"
        ))
    elif minimap.active:
      x = corner_x
      y = corner_y
    else:
      return []

    if not redrawn:
      redrawn = True
      minimap.sprite = minimap.render()

    sprites.append(Sprite(
      image=minimap.sprite,
      pos=(x, y),
      layer="hud"
    ))
    return sprites
