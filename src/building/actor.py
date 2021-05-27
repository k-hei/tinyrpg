from anims.walk import WalkAnim
from pygame import Rect
from config import TILE_SIZE
from filters import outline
from palette import WHITE

class Actor:
  speed = 1.5

  def __init__(actor, core, cell=None, facing=None, color=None, moving=False, move_period=30):
    actor.core = core
    actor.core.color = color
    actor.move_period = move_period
    actor.pos = (0, 0)
    actor.anim = None
    if cell:
      col, row = cell
      actor.pos = ((col + 0.5) * TILE_SIZE, (row + 0.5) * TILE_SIZE)
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
    actor.anim = WalkAnim(period=actor.move_period)
    actor.core.anims = [actor.anim]

  def stop_move(actor):
    actor.anim = None
    actor.core.anims = []

  def update(actor):
    if actor.anim:
      actor.anim.update()

  def render(actor):
    sprite = actor.core.render()
    sprite.image = outline(sprite.image, WHITE)
    sprite.origin = ("center", "center")
    x, y = actor.get_rect().midtop
    sprite.pos = (x, y - 1)
    return sprite
