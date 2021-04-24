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
from easing.expo import ease_out
from lerp import lerp

MARGIN_X = 8
MARGIN_Y = 6
SCALE = 3
ENTER_DURATION = 8
EXIT_DURATION = 4

class Minimap:
  def __init__(minimap, size):
    minimap.size = size
    minimap.time = 0
    minimap.active = False
    minimap.anim = None
    minimap.enter()

  def enter(minimap):
    minimap.active = True
    minimap.anim = TweenAnim(duration=ENTER_DURATION)

  def exit(minimap):
    minimap.active = False
    minimap.anim = TweenAnim(duration=EXIT_DURATION)

  def render(minimap, ctx):
    sprite_width, sprite_height = minimap.size
    scaled_size = (sprite_width * SCALE, sprite_height * SCALE)
    surface = Surface(scaled_size)
    surface.set_colorkey(0x123456)
    surface.fill(0x123456)
    temp_surface = Surface((sprite_width, sprite_height))
    temp_surface.set_colorkey(0x123456)
    temp_surface.fill(0x123456)
    pixels = PixelArray(temp_surface)
    minimap.time += 1

    hero = ctx.hero
    hero_x, hero_y = hero.cell
    floor = ctx.floor
    visible_cells = hero.visible_cells
    visited_cells = next((cells for floor, cells in ctx.memory if floor is ctx.floor), None)
    for cell in visited_cells:
      tile = ctx.floor.get_tile_at(cell)
      elem = ctx.floor.get_elem_at(cell)
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
      x = x - hero_x + sprite_width // 2
      y = y - hero_y + sprite_height // 2
      if color is not None and x >= 0 and y >= 0 and x < sprite_width and y < sprite_height:
        pixels[x, y] = color
    pixels.close()
    surface.blit(pygame.transform.scale(temp_surface, scaled_size), (0, 0))
    return surface

  def draw(minimap, surface, ctx):
    window_width = surface.get_width()
    window_height = surface.get_height()
    sprite = minimap.render(ctx)
    start_x = window_width
    target_x = start_x - sprite.get_width() - MARGIN_X
    if minimap.anim:
      t = minimap.anim.update()
      if minimap.active:
        t = ease_out(t)
      else:
        start_x, target_x = (target_x, start_x)
      x = lerp(start_x, target_x, t)
      if minimap.anim.done:
        minimap.anim = None
    elif minimap.active:
      x = target_x
    else:
      return
    surface.blit(sprite, (
      x,
      MARGIN_Y
    ))
