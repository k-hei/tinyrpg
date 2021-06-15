from math import sqrt
from pygame import Rect
from town.topview.element import Element
from anims.walk import WalkAnim
from config import TILE_SIZE
from filters import outline
from palette import WHITE

TALK_RADIUS = TILE_SIZE * 1.5

class Actor(Element):
  speed = 1.5
  spawn_offset = (8, 8)

  def __init__(actor, core, pos=None, facing=None, color=None, moving=False, move_period=30, is_shopkeep=False, message=None):
    super().__init__()
    actor.core = core
    actor.core.color = color
    actor.move_period = move_period
    actor.is_shopkeep = is_shopkeep
    actor.message = message
    actor.pos = pos
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

  def start_move(actor):
    actor.anim = WalkAnim(period=actor.move_period)
    actor.core.anims = [actor.anim]

  def stop_move(actor):
    actor.anim = None
    actor.core.anims = []

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
        and dist_y == -TILE_SIZE * 1.5
        and facing_y == -1)
    return in_range and dist_x * facing_x >= 0 and dist_y * facing_y >= 0

  def update(actor):
    if actor.anim:
      actor.anim.update()

  def view(actor, sprites):
    sprite = actor.core.render()
    # sprite.image = outline(sprite.image, WHITE)
    sprite.origin = ("center", "center")
    x, y = actor.get_rect().midtop
    sprite.pos = (x, y - 1)
    sprites.append(sprite)
