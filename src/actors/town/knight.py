import pygame
import config
import palette
from filters import replace_color
from assets import load as use_assets

class Knight:
  SPEED = 1.5

  def __init__(knight):
    knight.x = 0
    knight.facing = 1
    knight.walks = 0

  def move(knight, delta):
    if knight.facing != delta:
      knight.facing = delta
      knight.walks = 0
    knight.x += Knight.SPEED * delta
    knight.walks += 1
    if knight.x < 0:
      knight.x = 0
    if knight.x > config.window_width:
      knight.x = config.window_width

  def stop_move(knight):
    knight.walks = 0

  def render(knight):
    sprites = use_assets().sprites
    sprite = sprites["knight"]
    if knight.walks:
      if knight.walks % (config.MOVE_DURATION // 2) < config.MOVE_DURATION // 4:
        sprite = sprites["knight_walk"]
    sprite = replace_color(sprite, palette.BLACK, palette.BLUE)
    if knight.facing == -1:
      sprite = pygame.transform.flip(sprite, True, False)
    return sprite
