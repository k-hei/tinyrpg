from math import inf
from pygame import Rect

def find_bounds(cells):
  if not cells:
    return Rect(0, 0, 0, 0)
  left = inf
  top = inf
  right = -inf
  bottom = -inf
  for (x, y) in cells:
    if x < left:
      left = x
    if x > right:
      right = x
    if y < top:
      top = y
    if y > bottom:
      bottom = y
  return Rect(left, top, right - left + 1, bottom - top + 1)
