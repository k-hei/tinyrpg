from math import inf
from pygame import Rect

def find_bounds(cells):
  left = inf
  top = inf
  right = -inf
  bottom = -inf
  for (x, y) in cells:
    if x < left:
      left = x
    elif x > right:
      right = x
    if y < top:
      top = y
    elif y > bottom:
      bottom = y
  return Rect(left, top, right - left + 1, bottom - top + 1)
