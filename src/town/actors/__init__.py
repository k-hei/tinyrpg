from pygame.transform import flip
from config import TILE_SIZE, WINDOW_WIDTH
from sprite import Sprite

class Actor:
  SPEED = 1.5

  def __init__(actor, core):
    actor.core = core
    actor.x = 0
    actor.facing = 1
    actor.walks = 0
    actor.sprite = Sprite()

  def move(actor, delta):
    if actor.facing != delta:
      actor.facing = delta
      actor.walks = 0
    actor.x += Actor.SPEED * delta
    actor.walks += 1
    if actor.x <= -TILE_SIZE // 2:
      actor.x = -TILE_SIZE // 2
    if actor.x >= WINDOW_WIDTH + TILE_SIZE // 2:
      actor.x = WINDOW_WIDTH + TILE_SIZE // 2

  def stop_move(actor):
    actor.walks = 0

  def follow(actor, target):
    target_x = target.x - TILE_SIZE * target.facing
    if target_x < actor.x:
      actor.move(-1)
    elif target_x > actor.x:
      actor.move(1)
    else:
      actor.stop_move()
    if abs(target_x - actor.x) <= Actor.SPEED:
      actor.x = target_x

  def face(actor, facing):
    actor.facing = facing

  def render(actor):
    if actor.facing == -1:
      actor.sprite.image = flip(actor.sprite.image, True, False)
    return actor.sprite
