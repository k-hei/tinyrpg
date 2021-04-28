from math import ceil
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
BLACKOUT_DURATION = 10
BLACKOUT_DELAY = 60

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

  def render(minimap, t=None):
    if t is None:
      t = 1 if minimap.expanded else 0

    start_width, start_height = Minimap.SIZE_INIT
    end_width, end_height = minimap.parent.floor.size
    start_scale, end_scale = Minimap.SCALE_INIT, Minimap.SCALE_EXPAND

    sprite_width = lerp(start_width, end_width, t)
    sprite_height = lerp(start_height, end_height, t)
    sprite_scale = lerp(start_scale, end_scale, t)

    # requires: game.hero, game.floor, game.memory
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
      x = int(x - focus_x + sprite_width // 2)
      y = int(y - focus_y + sprite_height // 2)
      if x < 0 or y < 0 or x >= sprite_width or y >= sprite_height:
        continue
      tile = game.floor.get_tile_at(cell)
      elem = game.floor.get_elem_at(cell)
      color = None
      if type(elem) is Knight or type(elem) is Mage and cell in visible_cells:
        color = 0x3399FF if minimap.time % 60 >= 30 else 0x0066CC
      elif type(elem) is Mimic and cell in visible_cells:
        if elem.idle:
          color = 0xFFFF00 if minimap.time % 60 >= 30 else 0x7F7F00
        else:
          color = 0xFF0000 if minimap.time % 60 >= 30 else 0x990000
      elif isinstance(elem, Actor) and elem.faction == "enemy" and cell in visible_cells:
        if elem.ailment == "sleep":
          color = 0xCC0000
        else:
          color = 0xFF0000 if minimap.time % 60 >= 30 else 0x990000
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
        color = 0x00FF00 if minimap.time % 60 >= 30 else 0x007F00
      elif tile is Stage.STAIRS_DOWN:
        color = 0x007F00
      elif tile is Stage.PIT:
        if cell in visible_cells:
          color = 0x000000
      else:
        if cell in visible_cells:
          color = 0x333333
        else:
          color = 0x000000
      if color is not None:
        pixels[x, y] = color

    pixels.close()
    surface.blit(pygame.transform.scale(temp_surface, scaled_size), (0, 0))
    return surface

  def draw(minimap, surface):
    if minimap.sprite is None:
      minimap.sprite = minimap.render()
      redrawn = True
    else:
      redrawn = False

    corner_x = surface.get_width() - minimap.sprite.get_width() - MARGIN_X
    corner_y = MARGIN_Y
    center_x = surface.get_width() // 2 - minimap.sprite.get_width() // 2
    center_y = surface.get_height() // 2 - minimap.sprite.get_height() // 2
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

      if type(anim) in (ExpandAnim, ShrinkAnim):
        t = ease_in_out(t)
        redrawn = True
        if type(anim) is ExpandAnim:
          minimap.sprite = minimap.render(t)
        elif type(anim) is ShrinkAnim:
          minimap.sprite = minimap.render(1 - t)
        center_x = surface.get_width() // 2 - minimap.sprite.get_width() // 2
        center_y = surface.get_height() // 2 - minimap.sprite.get_height() // 2

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
      if minimap.expanded >= BLACKOUT_DELAY:
        t = min(1, (minimap.expanded - BLACKOUT_DELAY) / BLACKOUT_DURATION)
        alpha = int(t * 3) / 3 * 0xFF
        fill = Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(fill, (0, 0, 0, alpha), fill.get_rect())
        surface.blit(fill, (0, 0))
    elif minimap.active:
      x = corner_x
      y = corner_y
    else:
      return

    if not redrawn:
      redrawn = True
      minimap.sprite = minimap.render()

    surface.blit(minimap.sprite, (x, y))
