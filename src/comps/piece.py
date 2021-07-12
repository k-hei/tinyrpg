import math
import pygame
from pygame import Surface, Rect
from assets import load as use_assets
from filters import replace_color, outline
from colors.palette import WHITE

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
    if icon:
      icon = outline(icon, (0, 0, 0))
    cols, rows = Piece.get_size(blocks)
    surface = Surface((cols * Piece.BLOCK_SIZE, rows * Piece.BLOCK_SIZE)).convert_alpha()
    icon_pos = None

    def _connect(cell, other):
      col, row = cell
      x = col * Piece.BLOCK_SIZE
      y = row * Piece.BLOCK_SIZE
      rect = None
      width = 5
      height = 5
      if other == (col - 1, row):
        x -= 3
        pygame.draw.rect(surface, WHITE, Rect(x, y, width, Piece.BLOCK_SIZE - 1))
        pygame.draw.rect(surface, (0, 0, 0), Rect(x, y + 1, width, Piece.BLOCK_SIZE - 3))
        pygame.draw.rect(surface, color, Rect(x, y + 2, width, Piece.BLOCK_SIZE - 5))
      elif other == (col + 1, row):
        x += Piece.BLOCK_SIZE - 3
        pygame.draw.rect(surface, WHITE, Rect(x, y, width, Piece.BLOCK_SIZE - 1))
        pygame.draw.rect(surface, (0, 0, 0), Rect(x, y + 1, width, Piece.BLOCK_SIZE - 3))
        pygame.draw.rect(surface, color, Rect(x, y + 2, width, Piece.BLOCK_SIZE - 5))
      elif other == (col, row - 1):
        y -= 3
        pygame.draw.rect(surface, WHITE, Rect(x, y, Piece.BLOCK_SIZE - 1, height))
        pygame.draw.rect(surface, (0, 0, 0), Rect(x + 1, y, Piece.BLOCK_SIZE - 3, height))
        pygame.draw.rect(surface, color, Rect(x + 2, y, Piece.BLOCK_SIZE - 5, height))
      elif other == (col, row + 1):
        y += Piece.BLOCK_SIZE - 3
        pygame.draw.rect(surface, WHITE, Rect(x, y, Piece.BLOCK_SIZE - 1, height))
        pygame.draw.rect(surface, (0, 0, 0), Rect(x + 1, y, Piece.BLOCK_SIZE - 3, height))
        pygame.draw.rect(surface, color, Rect(x + 2, y, Piece.BLOCK_SIZE - 5, height))

    for i, cell in enumerate(blocks):
      col, row = cell
      x = col * Piece.BLOCK_SIZE
      y = row * Piece.BLOCK_SIZE
      if icon and i == 0:
        icon_pos = (x, y)
      n, e, w, s, ne, nw, se, sw = False, False, False, False, False, False, False, False
      for j, other in enumerate(blocks):
        if other == cell: continue
        if other == (col - 1, row):
          w = True
        elif other == (col + 1, row):
          e = True
        elif other == (col, row - 1):
          n = True
        elif other == (col, row + 1):
          s = True
        elif other == (col - 1, row - 1):
          nw = True
        elif other == (col + 1, row - 1):
          ne = True
        elif other == (col - 1, row + 1):
          sw = True
        elif other == (col + 1, row + 1):
          se = True
      sprite = assets.sprites["block"]
      if n and e and w and s: sprite = assets.sprites["block_news"]
      elif s and e and w: sprite = assets.sprites["block_sew"]
      elif n and w and s: sprite = assets.sprites["block_nws"]
      elif n and e and w: sprite = assets.sprites["block_new"]
      elif n and e and s: sprite = assets.sprites["block_nes"]
      elif n and e and ne: sprite = assets.sprites["block_nef"]
      elif e and s and se: sprite = assets.sprites["block_sef"]
      elif s and w and sw: sprite = assets.sprites["block_swf"]
      elif w and n and nw: sprite = assets.sprites["block_nwf"]
      elif n and e: sprite = assets.sprites["block_ne"]
      elif e and s: sprite = assets.sprites["block_se"]
      elif s and w: sprite = assets.sprites["block_sw"]
      elif w and n: sprite = assets.sprites["block_nw"]
      elif n and s: sprite = assets.sprites["block_ns"]
      elif e and w: sprite = assets.sprites["block_ew"]
      elif n: sprite = assets.sprites["block_n"]
      elif e: sprite = assets.sprites["block_e"]
      elif w: sprite = assets.sprites["block_w"]
      elif s: sprite = assets.sprites["block_s"]
      sprite = replace_color(sprite, 0xFFFF0000, color)
      surface.blit(sprite, (x, y))

    if icon_pos:
      x, y = icon_pos
      surface.blit(icon, (
        x + Piece.BLOCK_SIZE // 2 - icon.get_width() // 2 - 1,
        y + Piece.BLOCK_SIZE // 2 - icon.get_height() // 2 - 1
      ))

    return surface
