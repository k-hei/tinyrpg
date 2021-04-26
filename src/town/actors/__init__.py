import pygame
import config
import palette

class Actor:
  SPEED = 1.5

  def __init__(actor, name=None):
    actor.name = name
    actor.x = 0
    actor.facing = 1
    actor.walks = 0
    actor.dead = False

  def move(actor, delta):
    if actor.facing != delta:
      actor.facing = delta
      actor.walks = 0
    actor.x += Actor.SPEED * delta
    actor.walks += 1
    if actor.x <= -config.TILE_SIZE // 2:
      actor.x = -config.TILE_SIZE // 2
    if actor.x >= config.WINDOW_WIDTH + config.TILE_SIZE // 2:
      actor.x = config.WINDOW_WIDTH + config.TILE_SIZE // 2

  def stop_move(actor):
    actor.walks = 0

  def follow(actor, target):
    target_x = target.x - config.TILE_SIZE * target.facing
    if target_x < actor.x:
      actor.move(-1)
    elif target_x > actor.x:
      actor.move(1)
    else:
      actor.stop_move()
    if abs(target_x - actor.x) <= Actor.SPEED:
      actor.x = target_x

  def render(actor, sprite):
    if actor.facing == -1:
      sprite = pygame.transform.flip(sprite, True, False)
    return (sprite, 0, 0)
