from pygame.transform import flip
from config import TILE_SIZE, WINDOW_WIDTH, MOVE_DURATION
from sprite import Sprite
from anims.walk import WalkAnim

class Actor:
  XSPEED = 1.5
  YSPEED_NORTH = 0.65
  YSPEED_SOUTH = 0.75

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
    if delta_y == -1:
      actor.y -= Actor.YSPEED_NORTH
    elif delta_y == 1:
      actor.y += Actor.YSPEED_SOUTH
    if actor.facing != delta or actor.anim is None:
      actor.facing = delta
      actor.core.facing = delta
      actor.anim = WalkAnim(period=(MOVE_DURATION if delta_x else 30))
      actor.core.anims = [actor.anim]
    actor.anim.update()

  def stop_move(actor):
    actor.core.anims = []
    actor.anim = None

  def move_to(actor, target):
    target_x, target_y = target
    delta_x, delta_y = 0, 0
    if actor.x == target_x and actor.y == target_y:
      actor.stop_move()
      return True
    near_x = abs(target_x - actor.x) < Actor.XSPEED
    near_y = (abs(target_y - actor.y) < Actor.YSPEED_NORTH and target_y < actor.y
      or abs(target_y - actor.y) < Actor.YSPEED_SOUTH and target_y > actor.y)
    if target_x < actor.x:
      delta_x = -1
    elif target_x > actor.x:
      delta_x = 1
    if target_y < actor.y:
      delta_y = -1
    elif target_y > actor.y:
      delta_y = 1
    if delta_x or delta_y:
      actor.move((delta_x, delta_y))
    if near_x:
      actor.x = target_x
    if near_y:
      actor.y = target_y
    return False

  def get_follow_pos(actor):
    facing_x, facing_y = actor.facing
    target_x, target_y = actor.x, actor.y
    if facing_x:
      target_x = actor.x - TILE_SIZE * facing_x
    elif facing_y:
      target_y = actor.y - TILE_SIZE // 2 * facing_y
    return (target_x, target_y)

  def follow(actor, target, free=False):
    facing_x, facing_y = target.facing
    target_x, target_y = target.get_follow_pos()
    if not free and target_x != actor.x:
      target_y = actor.y
      facing_y = 0
    if actor.x == target_x and actor.y == target_y:
      return True
    return actor.move_to((target_x, target_y))

  def face(actor, facing):
    if isinstance(facing, Actor):
      facing = ((facing.x - actor.x) // (abs(facing.x - actor.x) or 1), actor.facing[1])
      return actor.face(facing)
    actor.facing = facing
    actor.core.facing = facing

  def render(actor):
    return actor.sprite
