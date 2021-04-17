import math
from pygame import Surface
from assets import load as use_assets
from filters import replace_color
import palette

class Piece:
  BLOCK_SIZE = 16

  def get_size(blocks):
    left = math.inf
    right = 0
    top = math.inf
    bottom = 0
    for x, y in blocks:
      if x < left:
        left = x
      if x > right:
        right = x
      if y < top:
        top = y
      if y > bottom:
        bottom = y
    return right - left + 1, bottom - top + 1

  def offset(blocks, delta):
    delta_x, delta_y = delta
    return [(x + delta_x, y + delta_y) for x, y in blocks]

  def render(blocks, color=None):
    assets = use_assets()
    sprite = assets.sprites["block"]
    if color:
      sprite = replace_color(sprite, palette.PURPLE, color)
    cols, rows = Piece.get_size(blocks)
    surface = Surface((cols * Piece.BLOCK_SIZE, rows * Piece.BLOCK_SIZE))
    surface.set_colorkey(0xFF00FF)
    surface.fill(0xFF00FF)
    for col, row in blocks:
      surface.blit(sprite, (col * Piece.BLOCK_SIZE, row * Piece.BLOCK_SIZE))
    return surface
