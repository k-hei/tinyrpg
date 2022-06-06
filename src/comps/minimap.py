from math import ceil
import pygame
from pygame import Surface, Rect, PixelArray
from pygame.transform import scale
from dungeon.stage import Stage
from dungeon.actors import DungeonActor
from dungeon.actors.npc import Npc
from dungeon.props.chest import Chest
from dungeon.props.rarechest import RareChest
from dungeon.props.coffin import Coffin
from dungeon.props.vase import Vase
from dungeon.props.itemdrop import ItemDrop
from dungeon.props.soul import Soul
from dungeon.props.door import Door
from dungeon.props.secretdoor import SecretDoor
from dungeon.props.altar import Altar
import locations.default.tileset as tileset
from colors.palette import GREEN, DARKGREEN, VIOLET, DARKVIOLET
from anims.tween import TweenAnim
from anims.warpin import WarpInAnim
from easing.expo import ease_out, ease_in_out
from lib.lerp import lerp
from lib.bounds import find_bounds
from lib.cell import subtract as subtract_vector
from lib.sprite import Sprite
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_SIZE, DEBUG_GEN, ENABLED_MINIMAP
import debug

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
COLOR_FLOOR = 0x004422
COLOR_FLOOR_DARK = 0x002200
COLOR_WALL = 0x00CC66
COLOR_WALL_DARK = 0x006633
COLOR_DOOR = 0x009966
COLOR_DOOR_DARK = 0x006633
COLOR_OASIS = 0x000066
COLOR_OASIS_DARK = 0x000033

class EnterAnim(TweenAnim):
  duration = ENTER_DURATION

class ExitAnim(TweenAnim):
  duration = EXIT_DURATION

class ExpandAnim(TweenAnim):
  duration = EXPAND_DURATION

class ShrinkAnim(TweenAnim):
  duration = SHRINK_DURATION

class Minimap:
  SIZE_INIT = (16, 16)
  SCALE_INIT = 3
  SCALE_EXPAND = 5
  BLACKOUT_DELAY = 120

  def render_surface(floor, size=None, focus=None, visible_cells=None, visited_cells=None, anims=[], blink=False):
    floor_width, floor_height = floor.size
    filled = not visible_cells and not visited_cells
    visible_cells = visible_cells or [(x, y) for y in range(floor.height) for x in range(floor.width)]
    visited_cells = visited_cells or visible_cells or []
    bounds = filled and Rect((0, 0), floor.size) or find_bounds(visited_cells)
    sprite_size = tuple(map(ceil, size or bounds.size))
    sprite_width, sprite_height = sprite_size

    surface = Surface(sprite_size)
    surface.fill(COLOR_WALL if filled else COLOR_KEY)
    surface.set_colorkey(COLOR_KEY)
    pixels = PixelArray(surface)

    focus_x, focus_y = focus or (floor_width // 2, floor_height // 2)
    window_left = int(focus_x - sprite_width / 2)
    window_top = int(focus_y - sprite_height / 2)
    window_right = window_left + sprite_width
    window_bottom = window_top + sprite_height

    for row in range(window_top, window_bottom):
      for col in range(window_left, window_right):
        if col < 0 or row < 0 or col >= floor_width or row >= floor_height:
          continue

        cell = (col, row)
        if cell not in visited_cells:
          continue

        tile = floor.get_tile_at(cell)

        if focus:
          focus_x, focus_y = focus
          x = int(col - focus_x + sprite_width / 2)
          y = int(row - focus_y + sprite_height / 2)
          if x < 0 or y < 0 or x >= sprite_width or y >= sprite_height:
            continue
        else:
          x, y = col, row

        is_cell_visible = cell in visible_cells
        elem = next((e for e in reversed(floor.get_elems_at(cell))), None)
        if elem and next((a for g in anims for a in g if type(a) is WarpInAnim and a.target is elem), None):
          elem = None

        # f(floor, cell, visible_cells=None, blink=False) -> color
        color = None
        if elem:
          if isinstance(elem, DungeonActor):
            if elem.faction == "player" and is_cell_visible:
              color = (0x3399FF, 0x0066CC)[blink]
            elif elem.faction == "ally" and is_cell_visible:
              color = (0x33FF99, 0x00CC66)[blink]
            elif elem.faction == "enemy" and is_cell_visible:
              if elem.ailment == "sleep":
                color = 0x990000
              elif elem.aggro:
                color = 0xFF0000
              else:
                color = (0xFF0000, 0x990000)[blink]
          elif isinstance(elem, Soul) and is_cell_visible:
            color = (VIOLET, DARKVIOLET)[blink]
          elif isinstance(elem, Npc) and is_cell_visible:
            color = (GREEN, DARKGREEN)[blink]
          elif isinstance(elem, Chest) and elem.rare:
            if elem.opened:
              color = 0x7F007F
            else:
              color = (0xFF00FF, 0x7F007F)[blink]
          elif isinstance(elem, (Chest, RareChest, Coffin, Vase)):
            if elem.opened:
              color = 0x7F7F00
            else:
              color = (0xFFFF00, 0x7F7F00)[blink]
          elif type(elem) is ItemDrop:
            color = (0xFFFF00, 0x7F7F00)[blink]
          elif type(elem) is Altar:
            color = (0xFFFF00, 0x7F7F00)[blink]
          elif isinstance(elem, SecretDoor) and elem.hidden:
            color = COLOR_WALL if is_cell_visible else COLOR_WALL_DARK
          elif isinstance(elem, Door) and not elem.opened:
            color = COLOR_DOOR if is_cell_visible else COLOR_DOOR_DARK
          elif isinstance(elem, Door) and elem.opened:
            color = COLOR_FLOOR if is_cell_visible else COLOR_FLOOR_DARK
          elif elem.solid:
            color = COLOR_WALL if is_cell_visible else COLOR_WALL_DARK
          else:
            color = COLOR_FLOOR if is_cell_visible else COLOR_FLOOR_DARK
        elif tile is Stage.STAIRS_UP:
          color = (0x00FF00, 0x007F00)[blink]
        elif tile is Stage.STAIRS_DOWN:
          color = 0x007F00
        elif floor.is_tile_at_pit(cell):
          if is_cell_visible:
            color = None # 0x000000
        elif (floor.is_tile_at_wall(cell)
        or floor.is_tile_at_of_type(cell, tileset.Hallway) and SecretDoor.exists_at(floor, (col, row + 1))):
          if is_cell_visible:
            if filled:
              continue
            color = COLOR_WALL
          else:
            color = COLOR_WALL_DARK
        elif floor.is_tile_at_oasis(cell):
          color = COLOR_OASIS if is_cell_visible else COLOR_OASIS_DARK
        else:
          color = COLOR_FLOOR if is_cell_visible else COLOR_FLOOR_DARK

        if color is not None:
          try:
            pixels[x, y] = color
          except IndexError:
            print((x, y), sprite_size)
            raise

    pixels.close()
    return surface

  def __init__(minimap, parent=None):
    minimap.parent = parent
    minimap.focus = None
    minimap.time = 0
    minimap.active = False
    minimap.expanded = 0
    minimap.sprite = None
    minimap.anims = []
    minimap.cache_hero_cell = None

  def enter(minimap, on_end=None):
    minimap.active = True
    minimap.anims.append(EnterAnim(on_end=on_end))

  def exit(minimap, on_end=None):
    minimap.active = False
    minimap.anims.append(ExitAnim(on_end=on_end))

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

    # requires: hero, stage, visited cells, animations?
    # - isn't this identical to what the stage view requires?
    # - if we wanted to coalesce these into an isolated store,
    #     we'd need to name it so it's easier to pass down
    # - could try passing in args on init by reference
    # - hero and stage will change

    # updates whenever any of the following occur:
    # - data changes
    # - visited cells change
    # - camera position (hero cell) changes

    game = minimap.parent
    floor = game.stage
    hero = game.hero
    if not hero or not hero.cell:
      return minimap.sprite
    visited_cells = game.visited_cells
    visible_cells = hero.visible_cells

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
      anims=[], # game.anims,
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

  def update(minimap):
    anim = minimap.anims[0] if minimap.anims else None
    if anim:
      anim.update()
      if anim.done:
        minimap.anims.pop(0)

    hero_cell = minimap.parent.hero and minimap.parent.hero.cell
    if hero_cell != minimap.cache_hero_cell:
      minimap.cache_hero_cell = hero_cell
      minimap.sprite = None

  def view(minimap):
    if not ENABLED_MINIMAP:
      return []

    sprites = []
    minimap.time += 1

    if minimap.sprite is None:
      minimap.sprite = minimap.render()
      redrawn = True
    else:
      redrawn = False

    if minimap.sprite is None:
      return []

    corner_x = WINDOW_WIDTH - minimap.sprite.get_width() - MARGIN_X
    corner_y = MARGIN_Y
    center_x = WINDOW_WIDTH // 2 - minimap.sprite.get_width() // 2
    center_y = WINDOW_HEIGHT // 2 - minimap.sprite.get_height() // 2
    anim = minimap.anims[0] if minimap.anims else None
    if anim:
      t = anim.pos
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

    if not redrawn and not minimap.time % 30:
      redrawn = True
      minimap.sprite = minimap.render()

    sprites.append(Sprite(
      image=minimap.sprite,
      pos=(x, y),
      layer="hud"
    ))
    return sprites
