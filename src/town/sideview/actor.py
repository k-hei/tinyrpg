from filters import outline
from palette import WHITE
from anims.walk import WalkAnim

class Actor:
  XSPEED = 1.5
  YSPEED_NORTH = 0.65
  YSPEED_SOUTH = 0.75
  MOVE_DURATION = 20

  def __init__(actor, core, color=None, facing=None, message=None):
    actor.pos = None
    actor.core = core
    actor.core.color = color
    actor.facing = facing
    actor.message = message
    actor.anim = None

  def get_name(actor):
    return actor.core.name

  def get_faction(actor):
    return actor.core.faction

  def get_facing(actor):
    return actor.core.facing

  def face(actor, facing):
    if type(facing) is tuple:
      actor.core.facing = facing
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
      actor_y -= Actor.YSPEED_NORTH
    elif delta_y == 1:
      actor_y += Actor.YSPEED_SOUTH
    actor.pos = (actor_x, actor_y)
    actor.face(delta)
    if not actor.core.anims:
      actor.start_move()

  def start_move(actor):
    actor.anim = WalkAnim(period=Actor.MOVE_DURATION)
    actor.core.anims = [actor.anim]

  def stop_move(actor):
    actor.anim = None
    actor.core.anims = []

  def update(actor):
    if actor.anim:
      actor.anim.update()

  def view(actor):
    actor_sprites = actor.core.view()
    actor_sprite = actor_sprites[0]
    actor_sprite.image = outline(actor_sprite.image, WHITE)
    actor_sprite.move(actor.pos)
    actor_sprite.origin = ("center", "center")
    return actor_sprites
