from math import ceil
import pygame
from pygame import Surface, Rect, PixelArray
from dungeon.stage import Stage
from dungeon.actors.knight import Knight
from dungeon.actors import DungeonActor
from dungeon.actors.mage import Mage
from dungeon.actors.mimic import Mimic
from dungeon.actors.npc import Npc
from dungeon.props.chest import Chest
from dungeon.props.soul import Soul
import palette
from palette import GREEN, GREEN_DARK, PURPLE, PURPLE_DARK
from anims.tween import TweenAnim
from easing.expo import ease_out, ease_in_out
from lib.lerp import lerp
from sprite import Sprite
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_SIZE

MARGIN_X = 8
MARGIN_Y = 6
ENTER_DURATION = 8
EXIT_DURATION = 4
EXPAND_DURATION = 15
SHRINK_DURATION = 10
BLACKOUT_DURATION = 10
BLACKOUT_DELAY = 60
BLACKOUT_FRAMES = 3

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

  def __init__(minimap, parent):
    minimap.parent = parent
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

    start_width, start_height = Minimap.SIZE_INIT
    end_width, end_height = minimap.parent.floor.size
    start_scale, end_scale = Minimap.SCALE_INIT, Minimap.SCALE_EXPAND

    sprite_width = lerp(start_width, end_width, t)
    sprite_height = lerp(start_height, end_height, t)
    sprite_scale = lerp(start_scale, end_scale, t)

    # requires: game.hero, game.floor, game.memory?
    game = minimap.parent
    hero = game.hero
    start_x, start_y = hero.cell
    end_x, end_y = sprite_width // 2, sprite_height // 2
    focus_x = round(lerp(start_x, end_x, t))
    focus_y = round(lerp(start_y, end_y, t))

    scaled_width = round(sprite_width * sprite_scale)
    scaled_height = round(sprite_height * sprite_scale)
    scaled_size = (scaled_width, scaled_height)
    surface = Surface(scaled_size)
    surface.set_colorkey(0x123456)
    surface.fill(0x123456)
    temp_surface = Surface((ceil(sprite_width), ceil(sprite_height)))
    temp_surface.set_colorkey(0x123456)
    temp_surface.fill(0x123456)
    pixels = PixelArray(temp_surface)
    minimap.time += 1

    floor = game.floor
    visible_cells = hero.visible_cells
    visited_cells = next((cells for floor, cells in game.memory if floor is game.floor), None)
    for cell in visited_cells:
      x, y = cell
      tile = game.floor.get_tile_at(cell)
      tile_above = game.floor.get_tile_at((x, y - 1))
      tile_below = game.floor.get_tile_at((x, y + 1))
      x = int(x - focus_x + sprite_width // 2)
      y = int(y - focus_y + sprite_height // 2)
      if x < 0 or y < 0 or x >= sprite_width or y >= sprite_height:
        continue
      elem = game.floor.get_elem_at(cell)
      color = None
      if type(elem) is Knight or type(elem) is Mage and cell in visible_cells:
        color = 0x3399FF if minimap.time % 60 >= 30 else 0x0066CC
      elif type(elem) is Mimic and cell in visible_cells:
        if elem.idle:
          color = 0xFFFF00 if minimap.time % 60 >= 30 else 0x7F7F00
        else:
          color = 0xFF0000 if minimap.time % 60 >= 30 else 0x990000
      elif isinstance(elem, DungeonActor) and elem.get_faction() == "enemy" and cell in visible_cells:
        if elem.ailment == "sleep":
          color = 0x990000
        else:
          color = 0xFF0000 if minimap.time % 60 >= 30 else 0x990000
      elif isinstance(elem, Soul) and cell in visible_cells:
        color = PURPLE if minimap.time % 60 >= 30 else PURPLE_DARK
      elif isinstance(elem, Npc) and cell in visible_cells:
        color = GREEN if minimap.time % 60 >= 30 else GREEN_DARK
      elif type(elem) is Chest and elem.rare:
        if elem.opened:
          color = 0x7F007F
        else:
          color = 0xFF00FF if minimap.time % 60 >= 30 else 0x7F007F
      elif type(elem) is Chest:
        if elem.opened:
          color = 0x7F7F00
        else:
          color = 0xFFFF00 if minimap.time % 60 >= 30 else 0x7F7F00
      elif tile is Stage.WALL or tile is Stage.DOOR_HIDDEN or tile is Stage.DOOR_LOCKED or (
      tile is Stage.DOOR_WAY and (tile_above is Stage.DOOR_HIDDEN or tile_below is Stage.DOOR_HIDDEN)):
        if cell in visible_cells:
          color = 0x00CCFF
        else:
          color = 0x0066CC
      elif tile is Stage.DOOR:
        if cell in visible_cells:
          color = 0x0066CC
        else:
          color = 0x0033CC
      elif tile is Stage.DOOR_OPEN:
        if cell in visible_cells:
          color = 0x003399
        else:
          color = 0x003399
      elif tile is Stage.STAIRS_UP:
        color = 0x00FF00 if minimap.time % 60 >= 30 else 0x007F00
      elif tile is Stage.STAIRS_DOWN:
        color = 0x007F00
      elif tile is Stage.PIT:
        if cell in visible_cells:
          color = 0x000033
      elif tile is Stage.FLOOR_ELEV or tile is Stage.WALL_ELEV or tile is Stage.STAIRS:
        if cell in visible_cells:
          color = 0x4D4D4D
        else:
          color = 0x242424
      else:
        if cell in visible_cells:
          color = 0x003399
        else:
          color = 0x000066
      if color is not None:
        pixels[x, y] = color

    pixels.close()
    surface.blit(pygame.transform.scale(temp_surface, scaled_size), (0, 0))
    return surface

  def view(minimap):
    sprites = []
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
      return

    if not redrawn:
      redrawn = True
      minimap.sprite = minimap.render()

    sprites.append(Sprite(
      image=minimap.sprite,
      pos=(x, y),
      layer="hud"
    ))
    return sprites
