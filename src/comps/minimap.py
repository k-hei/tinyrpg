import pygame
from pygame import Surface, Rect, PixelArray
from stage import Stage
from actors.knight import Knight
from actors import Actor
from actors.mage import Mage
from actors.mimic import Mimic
from props.chest import Chest
import palette
from anims.tween import TweenAnim
from easing.expo import ease_out, ease_in_out
from lerp import lerp

MARGIN_X = 8
MARGIN_Y = 6
ENTER_DURATION = 8
EXIT_DURATION = 4
EXPAND_DURATION = 15
SHRINK_DURATION = 10

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

  def __init__(minimap, parent):
    minimap.parent = parent
    minimap.size = Minimap.SIZE_INIT
    minimap.scale = Minimap.SCALE_INIT
    minimap.time = 0
    minimap.active = False
    minimap.expanded = False
    minimap.anims = []
    minimap.enter()

  def enter(minimap):
    minimap.active = True
    minimap.anims.append(EnterAnim())

  def exit(minimap):
    minimap.active = False
    minimap.anims.append(ExitAnim())

  def expand(minimap):
    minimap.size = minimap.parent.floor.size
    minimap.scale = Minimap.SCALE_EXPAND
    minimap.expanded = True
    minimap.anims.append(ExpandAnim())

  def shrink(minimap):
    minimap.size = Minimap.SIZE_INIT
    minimap.scale = Minimap.SCALE_INIT
    minimap.expanded = False
    minimap.anims.append(ShrinkAnim())

  def render(minimap):
    sprite_width, sprite_height = minimap.size
    scaled_size = (sprite_width * minimap.scale, sprite_height * minimap.scale)
    surface = Surface(scaled_size)
    surface.set_colorkey(0x123456)
    surface.fill(0x123456)
    temp_surface = Surface(minimap.size)
    temp_surface.set_colorkey(0x123456)
    temp_surface.fill(0x123456)
    pixels = PixelArray(temp_surface)
    minimap.time += 1

    # requires: game.hero, game.floor, game.memory
    game = minimap.parent
    hero = game.hero
    focus_x, focus_y = hero.cell
    if minimap.expanded:
      focus_x = sprite_width // 2
      focus_y = sprite_height // 2

    floor = game.floor
    visible_cells = hero.visible_cells
    visited_cells = next((cells for floor, cells in game.memory if floor is game.floor), None)
    for cell in visited_cells:
      tile = game.floor.get_tile_at(cell)
      elem = game.floor.get_elem_at(cell)
      color = None
      if type(elem) is Knight or type(elem) is Mage and cell in visible_cells:
        color = 0x337FFF
      elif type(elem) is Mimic and cell in visible_cells:
        if elem.idle:
          color = 0xFFFF00 if minimap.time % 60 >= 30 else 0x7F7F00
        else:
          color = 0xFF0000
      elif isinstance(elem, Actor) and elem.faction == "enemy" and cell in visible_cells:
        if elem.ailment == "sleep":
          color = 0xFF00FF
        else:
          color = 0xFF0000
      elif type(elem) is Chest:
        if elem.opened:
          color = 0x7F7F00
        elif cell in visible_cells:
          color = 0xFFFF00 if minimap.time % 60 >= 30 else 0x7F7F00
        else:
          color = 0xFFFF00
      elif tile is Stage.WALL or tile is Stage.DOOR_HIDDEN or tile is Stage.DOOR_LOCKED:
        if cell in visible_cells:
          color = 0xFFFFFF
        else:
          color = 0x7F7F7F
      elif tile is Stage.DOOR:
        if cell in visible_cells:
          color = 0x7F7F7F
        else:
          color = 0x333333
      elif tile is Stage.DOOR_OPEN:
        if cell in visible_cells:
          color = 0x333333
        else:
          color = 0x333333
      elif tile is Stage.STAIRS_UP:
        if cell in visible_cells:
          color = 0x00FF00 if minimap.time % 60 >= 30 else 0x007F00
        else:
          color = 0x00FF00
      elif tile is Stage.STAIRS_DOWN:
        if cell in visible_cells:
          color = 0xFFFFFF
        else:
          color = 0x7F7F7F
      elif tile is Stage.PIT:
        if cell in visible_cells:
          color = 0x000000
      else:
        if cell in visible_cells:
          color = 0x333333
        else:
          color = 0x000000
      x, y = cell
      x = x - focus_x + sprite_width // 2
      y = y - focus_y + sprite_height // 2
      if color is not None and x >= 0 and y >= 0 and x < sprite_width and y < sprite_height:
        pixels[x, y] = color

    pixels.close()
    surface.blit(pygame.transform.scale(temp_surface, scaled_size), (0, 0))
    return surface

  def draw(minimap, surface):
    sprite = minimap.render()
    corner_x = surface.get_width() - sprite.get_width() - MARGIN_X
    corner_y = MARGIN_Y
    center_x = surface.get_width() // 2 - sprite.get_width() // 2
    center_y = surface.get_height() // 2 - sprite.get_height() // 2
    anim = minimap.anims[0] if minimap.anims else None
    if anim:
      t = anim.update()
      if type(anim) is EnterAnim:
        t = ease_out(t)
        start_x, start_y = surface.get_width(), corner_y
        target_x, target_y = corner_x, corner_y
      elif type(anim) is ExitAnim:
        start_x, start_y = corner_x, corner_y
        target_x, target_y = surface.get_width(), corner_y
      elif type(anim) is ExpandAnim:
        t = ease_in_out(t)
        start_x, start_y = corner_x, corner_y
        target_x, target_y = center_x, center_y
      elif type(anim) is ShrinkAnim:
        t = ease_in_out(t)
        start_x, start_y = center_x, center_y
        target_x, target_y = corner_x, corner_y
      x = lerp(start_x, target_x, t)
      y = lerp(start_y, target_y, t)
      if anim.done:
        minimap.anims.pop(0)
    elif minimap.expanded:
      x = center_x
      y = center_y
    elif minimap.active:
      x = corner_x
      y = corner_y
    else:
      return

    surface.blit(sprite, (x, y))
