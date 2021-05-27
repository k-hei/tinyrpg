from pygame import Rect
from config import TILE_SIZE

class Element:
  def __init__(elem, solid=True):
    elem.pos = (0, 0)
    elem.solid = solid

  def get_rect(elem):
    x, y = elem.pos
    left = x - TILE_SIZE // 2
    top = y - TILE_SIZE // 2
    return Rect(left, top, TILE_SIZE, TILE_SIZE)

  def effect(elem, ctx):
    pass

  def reset_effect(elem):
    pass

  def update(elem):
    pass
