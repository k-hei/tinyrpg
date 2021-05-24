from pygame.transform import flip
from config import TILE_SIZE, WINDOW_WIDTH
from sprite import Sprite
from anims.walk import WalkAnim

class Actor:
  XSPEED = 1.5
  YSPEED = 0.75

  def __init__(actor, core):
    actor.core = core
    actor.x = 0
    actor.y = 0
    actor.facing = (1, 0)
    actor.anim = None
    actor.sprite = Sprite()

  def get_name(actor):
    return actor.core.name

  def move(actor, delta):
    delta_x, delta_y = delta
    if delta_x:
      actor.x += Actor.XSPEED * delta_x
    elif delta_y:
      actor.y += Actor.YSPEED * delta_y
    if actor.facing != delta or actor.anim is None:
      actor.facing = delta
      actor.core.facing = delta
      actor.anim = WalkAnim()
      actor.core.anims.append(actor.anim)
    actor.anim.update()

  def stop_move(actor):
    if actor.anim in actor.core.anims:
      actor.core.anims.remove(actor.anim)
    actor.anim = None

  def move_to(actor, target):
    target_x, target_y = target
    if abs(target_y - actor.y) <= Actor.YSPEED:
      actor.y = target_y
    elif target_y < actor.y:
      actor.move((0, -1))
    elif target_y > actor.y:
      actor.move((0, 1))
    if abs(target_x - actor.x) <= Actor.XSPEED:
      actor.x = target_x
    elif target_x < actor.x:
      actor.move((-1, 0))
    elif target_x > actor.x:
      actor.move((1, 0))
    if actor.x == target_x and actor.y == target_y:
      actor.stop_move()

  def follow(actor, target):
    target_x = target.x - TILE_SIZE * target.facing[0]
    actor.move_to((target_x, target.y))

  def face(actor, facing):
    actor.facing = facing
    actor.core.facing = facing

  def render(actor):
    return actor.sprite
