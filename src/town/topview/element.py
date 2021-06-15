from pygame import Rect
from config import TILE_SIZE

class Element:
  size = (TILE_SIZE, TILE_SIZE)
  spawn_offset = (0, 0)
  rect_offset = (-8, -8)

  def __init__(elem, solid=True):
    elem.pos = (0, 0)
    elem.spawn_pos = None
    elem.solid = solid

  def spawn(elem, pos):
    x, y = pos
    offset_x, offset_y = elem.spawn_offset
    elem.pos = (x + offset_x, y + offset_y)
    elem.spawn_pos = pos

  def get_rect(elem):
    x, y = elem.pos
    width, height = elem.size
    offset_x, offset_y = elem.rect_offset
    left = x + offset_x
    top = y + offset_y
    return Rect(left, top, width, height)

  def effect(elem, ctx):
    pass

  def reset_effect(elem):
    pass

  def update(elem):
    pass
