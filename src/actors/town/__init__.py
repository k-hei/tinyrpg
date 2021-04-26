import pygame
import config
import palette
from filters import replace_color

class Actor:
  SPEED = 1.5

  def __init__(actor):
    actor.x = 0
    actor.facing = 1
    actor.walks = 0

  def move(actor, delta):
    if actor.facing != delta:
      actor.facing = delta
      actor.walks = 0
    actor.x += Actor.SPEED * delta
    actor.walks += 1
    if actor.x < -config.TILE_SIZE // 2:
      actor.x = -config.TILE_SIZE // 2
    if actor.x > config.WINDOW_WIDTH + config.TILE_SIZE // 2:
      actor.x = config.WINDOW_WIDTH + config.TILE_SIZE // 2

  def stop_move(actor):
    actor.walks = 0

  def render(actor, sprite):
    sprite = replace_color(sprite, palette.BLACK, palette.BLUE)
    if actor.facing == -1:
      sprite = pygame.transform.flip(sprite, True, False)
    return sprite
