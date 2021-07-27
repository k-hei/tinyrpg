from pygame.transform import flip
from sprite import Sprite
from vfx import Vfx
import lib.vector as vector
import assets
from filters import replace_color
from anims.frame import FrameAnim
from colors.palette import BLACK, RED
from config import TILE_SIZE

def get_arrow_frames(direction):
  if direction == (-1, 0):
    frames = [flip(s, True, False) for s in assets.sprites["arrow_right"]]
  elif direction == (1, 0):
    frames = assets.sprites["arrow_right"]
  elif direction == (0, -1):
    frames = assets.sprites["arrow_up"]
  elif direction == (0, 1):
    frames = assets.sprites["arrow_down"]
  return [replace_color(f, BLACK, RED) for f in frames]

class ArrowAnim(FrameAnim):
  frames_duration = 7
  loop = True

class ArrowLeftAnim(ArrowAnim): frames = get_arrow_frames((-1, 0))
class ArrowRightAnim(ArrowAnim): frames = get_arrow_frames((1, 0))
class ArrowUpAnim(ArrowAnim): frames = get_arrow_frames((0, -1))
class ArrowDownAnim(ArrowAnim): frames = get_arrow_frames((0, 1))

class Arrow(Vfx):
  speed = 3

  def __init__(arrow, cell, direction, *args, **kwargs):
    super().__init__(pos=vector.scale(
      vector.add(cell, (0.5, 0.5), vector.scale(direction, 0.5)),
      scalar=TILE_SIZE
    ), *args, **kwargs)
    arrow.direction = direction
    arrow.anim = {
      (-1, 0): ArrowLeftAnim(),
      (1, 0): ArrowRightAnim(),
      (0, -1): ArrowUpAnim(),
      (0, 1): ArrowDownAnim(),
    }[direction]

  def update(arrow):
    arrow.pos = vector.add(arrow.pos, vector.scale(arrow.direction, arrow.speed))
    arrow.anim.update()

  def view(arrow):
    return [Sprite(
      image=arrow.anim.frame(),
      pos=arrow.pos,
      origin=("center", "center"),
      layer="vfx"
    )]
