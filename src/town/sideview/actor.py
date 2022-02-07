from lib.sprite import Sprite
from anims.walk import WalkAnim
from config import TILE_SIZE

class Actor:
  XSPEED = 1.5
  YSPEED_NORTH = 0.65
  YSPEED_SOUTH = 0.75
  MOVE_DURATION = 20
  INDOORS_HORIZON = -18
  scale = 1

  def __init__(actor, core, color=None, facing=None):
    actor.pos = None
    actor.core = core
    actor.core.color = color
    actor.facing = facing or actor.core.facing
    actor.anim = None
    actor.moved = False

  @property
  def name(actor):
    return actor.core.name

  @property
  def faction(actor):
    return actor.core.faction

  @property
  def facing(actor):
    return actor.core.facing

  @facing.setter
  def facing(actor, facing):
    actor.core.facing = facing

  @property
  def message(actor):
    return actor.core.message

  def face(actor, facing):
    if type(facing) is tuple:
      actor.facing = facing
      return
    if actor.pos == facing.pos:
      return actor.face((0, 1))
    target_x, target_y = facing.pos
    actor_x, actor_y = actor.pos
    if target_x < actor_x:
      actor.face((-1, 0))
    elif target_x > actor_x:
      actor.face((1, 0))

  def move(actor, delta):
    delta_x, delta_y = delta
    actor_x, actor_y = actor.pos
    if delta_x:
      actor_x += Actor.XSPEED * delta_x
    if delta_y == -1:
      if actor_y < Actor.INDOORS_HORIZON:
        actor_y -= Actor.YSPEED_NORTH / 2
      else:
        actor_y -= Actor.YSPEED_NORTH
    elif delta_y == 1:
      actor_y += Actor.YSPEED_SOUTH
    actor.pos = (actor_x, actor_y)
    actor.face(delta)
    if not actor.core.anims:
      actor.start_move()
    actor.moved = True

  def move_to(actor, target):
    if actor.pos == target:
      actor.stop_move()
      return True
    actor_x, actor_y = actor.pos
    target_x, target_y = target
    delta_x, delta_y = 0, 0
    if actor_x > target_x:
      delta_x = -1
    elif actor_x < target_x:
      delta_x = 1
    if actor_y > target_y:
      delta_y = -1
    elif actor_y < target_y:
      delta_y = 1
    if delta_x or delta_y:
      actor.move((delta_x, delta_y))
    actor_x, actor_y = actor.pos
    near_x = abs(target_x - actor_x) < Actor.XSPEED
    near_y = (abs(target_y - actor_y) < Actor.YSPEED_NORTH and target_y < actor_y
      or abs(target_y - actor_y) < Actor.YSPEED_SOUTH and target_y > actor_y)
    if near_x:
      actor.pos = (target_x, actor_y)
    if near_y:
      actor.pos = (actor_x, target_y)
    return False

  def start_move(actor):
    actor.anim = WalkAnim(period=Actor.MOVE_DURATION)
    actor.core.anims = [actor.anim]

  def stop_move(actor):
    actor.anim = None
    actor.core.anims = []

  def follow(actor, target, free=False, force=False):
    if actor.pos == target.pos:
      return True
    actor_x, actor_y = actor.pos
    target_x, target_y = target.pos
    facing_x, facing_y = target.facing
    dist_x = abs(target_x - actor_x)
    if not actor.moved and dist_x < TILE_SIZE and not force:
      return False
    if not free and target_x != actor_x:
      target_y = actor_y
      facing_y = 0
    if facing_x:
      target_x = target_x - TILE_SIZE * facing_x
    elif facing_y:
      target_y = target_y - TILE_SIZE // 2 * facing_y
    return actor.move_to((target_x, target_y))

  def recruit(actor):
    if actor.core.faction != "player":
      actor.core.faction = "player"
      return True
    else:
      return False

  def update(actor):
    if actor.anim:
      actor.anim.update()

  def view(actor):
    actor_sprites = actor.core.view()
    actor_sprite = actor_sprites[0]
    actor_sprite.move(actor.pos)
    actor_sprite.origin = Sprite.ORIGIN_CENTER
    actor_sprite.layer = "elems"
    return actor_sprites
