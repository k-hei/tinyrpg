from math import sqrt
from pygame import Rect
from town.topview.element import Element
from anims.walk import WalkAnim
from config import TILE_SIZE

TALK_RADIUS = TILE_SIZE

class Actor(Element):
  speed = 1.5
  spawn_offset = (8, 8)

  def __init__(actor, core, pos=None, facing=None, color=None, moving=False, move_period=30, spawn_offset=None, is_shopkeep=False, message=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    actor.core = core
    actor.core.color = color
    actor.move_period = move_period
    actor.spawn_offset = spawn_offset or Actor.spawn_offset
    actor.is_shopkeep = is_shopkeep
    actor.message = message
    actor.pos = pos
    actor.moved = False
    actor.anim = None
    if facing:
      actor.face(facing)
    if moving:
      actor.start_move()

  def get_rect(actor):
    x, y = actor.pos
    width = TILE_SIZE // 2
    height = TILE_SIZE // 2
    left = x - width // 2
    top = y
    return Rect(left, top, width, height)

  def get_name(actor):
    return actor.core.name

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
    dist_x = target_x - actor_x
    dist_y = target_y - actor_y
    dist = sqrt(dist_x * dist_x + dist_y * dist_y)
    norm_x = dist_x / dist
    norm_y = dist_y / dist
    facing_x = round(norm_x)
    facing_y = round(norm_y)
    actor.face((facing_x, facing_y))

  def move(actor, delta):
    delta_x, delta_y = delta
    x, y = actor.pos
    x += delta_x * actor.speed
    y += delta_y * actor.speed
    actor.pos = (x, y)
    actor.face(delta)
    if actor.anim is None:
      actor.start_move()
    actor.moved = True

  def move_to(actor, target):
    if actor.pos == target:
      actor.stop_move()
      return True
    actor_x, actor_y = actor.pos
    target_x, target_y = target
    delta_x, delta_y = 0, 0
    near_x = abs(target_x - actor_x) < actor.speed
    near_y = abs(target_y - actor_y) < actor.speed
    if actor_x > target_x and not near_x:
      delta_x = -1
    elif actor_x < target_x and not near_x:
      delta_x = 1
    if actor_y > target_y and not near_y:
      delta_y = -1
    elif actor_y < target_y and not near_y:
      delta_y = 1
    if near_x:
      actor.pos = (target_x, actor_y)
    if near_y:
      actor.pos = (actor_x, target_y)
    if delta_x or delta_y:
      actor.move((delta_x, delta_y))
    return False

  def start_move(actor):
    actor.anim = WalkAnim(period=actor.move_period)
    actor.core.anims = [actor.anim]

  def stop_move(actor):
    actor.anim = None
    actor.core.anims = []

  def follow(actor, target):
    if actor.pos == target.pos:
      return True
    actor_x, actor_y = actor.pos
    facing_x, facing_y = actor.get_facing()
    target_x, target_y = target.pos
    target_facing_x, target_facing_y = target.get_facing()
    dist_x = abs(target_x - actor_x)
    dist_y = abs(target_y - actor_y)
    if not actor.moved and dist_x < TILE_SIZE and dist_y < TILE_SIZE:
      return False
    if facing_x and dist_x and not (dist_x < TILE_SIZE and dist_y > TILE_SIZE):
      target_x = target_x - TILE_SIZE * target_facing_x
      target_y = actor_y
    elif facing_y and dist_y:
      target_x = actor_x
      target_y = target_y - TILE_SIZE * target_facing_y
    return actor.move_to((target_x, target_y))

  def next_message(actor):
    return actor.message

  def can_talk(actor, target):
    if actor is target or not isinstance(target, Actor) or not target.message:
      return False
    actor_x, actor_y = actor.pos
    target_x, target_y = target.pos
    dist_x = target_x - actor_x
    dist_y = target_y - actor_y
    facing_x, facing_y = actor.get_facing()
    in_range = (sqrt(dist_x * dist_x + dist_y * dist_y) < TALK_RADIUS
      or target.is_shopkeep
        and abs(dist_x) < TILE_SIZE // 2
        and dist_y == -TILE_SIZE
        and facing_y == -1)
    return in_range and dist_x * facing_x >= 0 and dist_y * facing_y >= 0

  def update(actor):
    if actor.anim:
      actor.anim.update()

  def view(actor):
    actor_sprites = actor.core.view()
    if not actor_sprites:
      return []
    actor_sprite = actor_sprites[0]
    actor_sprite.origin = ("center", "center")
    x, y = actor.get_rect().midtop
    actor_sprite.pos = (x, y - 1)
    return actor_sprites
