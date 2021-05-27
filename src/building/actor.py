from anims.walk import WalkAnim
from pygame import Rect
from config import TILE_SIZE

class Actor:
  speed = 1.5
  move_duration = 30

  def __init__(actor, core, cell=None, facing=None, color=None):
    actor.core = core
    actor.pos = (0, 0)
    actor.anim = None
    if cell is not None:
      col, row = cell
      actor.pos = ((col + 0.5) * TILE_SIZE, (row + 0.5) * TILE_SIZE)
    if facing is not None:
      actor.face(facing)
    if color:
      actor.core.color = color

  def get_rect(actor):
    x, y = actor.pos
    width = TILE_SIZE // 2
    height = TILE_SIZE // 2
    left = x - width // 2
    top = y
    return Rect(left, top, width, height)

  def face(actor, facing):
    actor.core.facing = facing

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
    actor.anim = WalkAnim(period=actor.move_duration)
    actor.core.anims = [actor.anim]

  def stop_move(actor):
    actor.anim = None
    actor.core.anims = []

  def update(actor):
    if actor.anim:
      actor.anim.update()

  def render(actor):
    sprite = actor.core.render()
    sprite.pos = actor.get_rect().midtop
    sprite.origin = ("center", "center")
    return sprite
