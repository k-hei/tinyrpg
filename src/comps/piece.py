import math
from pygame import Surface
from assets import load as use_assets
from filters import replace_color, outline
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

  def render(blocks, color=None, icon=None):
    assets = use_assets()
    block = assets.sprites["block"]
    if color:
      block = replace_color(block, palette.PURPLE, color)
    if icon:
      icon = outline(icon, (0, 0, 0))
    cols, rows = Piece.get_size(blocks)
    surface = Surface((cols * Piece.BLOCK_SIZE, rows * Piece.BLOCK_SIZE))
    surface.set_colorkey(0xFF00FF)
    surface.fill(0xFF00FF)
    icon_pos = None
    for i, (col, row) in enumerate(blocks):
      x = col * Piece.BLOCK_SIZE
      y = row * Piece.BLOCK_SIZE
      if icon and i == 0:
        icon_pos = (x, y)
      surface.blit(block, (x, y))
    if icon_pos:
      x, y = icon_pos
      surface.blit(icon, (
        x + Piece.BLOCK_SIZE // 2 - icon.get_width() // 2 - 1,
        y + Piece.BLOCK_SIZE // 2 - icon.get_height() // 2 - 1
      ))
    return surface
