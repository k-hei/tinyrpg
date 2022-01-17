from math import pi, sin, cos
from vfx import Vfx
from config import TILE_SIZE
import lib.vector as vector
from lib.sprite import Sprite
from lib.filters import replace_color
from anims import Anim
from anims.tween import TweenAnim
from anims.frame import FrameAnim
from cores.mage import Mage
from colors.palette import BLACK

class MageCloneVfx(Vfx):
  @staticmethod
  def transpose_angle(angle, item_count):
    # Assumes only 4 clones
    return (angle / pi / 0.5) / item_count * 2 * pi

  SPREAD_DISTANCE = 48
  SPREAD_DURATION = 30
  SPIN_DURATION = 90
  ADJUST_DURATION = 30
  ROTATE_PERIOD = 75

  class SpreadAnim(TweenAnim): pass
  class PauseAnim(Anim): pass
  class AdjustAnim(TweenAnim): pass

  def __init__(fx, cell, angle, animated=True, on_ready=None, *args, **kwargs):
    x, y = cell
    super().__init__(
      kind=None,
      pos=((x + 0.5) * TILE_SIZE, (y + 1) * TILE_SIZE),
      *args,
      **kwargs
    )
    fx.pos_start = fx.pos
    fx.angle = angle
    fx.cell = cell
    fx.anims = [
      [Mage.CastAnim()],
      [
        fx.SpreadAnim(duration=fx.SPREAD_DURATION),
        fx.PauseAnim(duration=fx.SPIN_DURATION),
        fx.AdjustAnim(
          duration=fx.ADJUST_DURATION,
          target=(fx.angle, fx.transpose_angle(fx.angle, item_count=5))
        ),
        fx.PauseAnim(duration=fx.SPIN_DURATION, on_end=lambda: (
          on_ready and on_ready(fx)
        )),
      ] if animated else []
    ]

  def update(fx, *_):
    fx.update_anims()
    spread_progress = next((a.pos for g in fx.anims for a in g if type(a) is fx.SpreadAnim), 1)
    fx.pos = vector.add(fx.pos_start, (
      cos(fx.angle) * fx.SPREAD_DISTANCE * spread_progress,
      sin(fx.angle) * fx.SPREAD_DISTANCE * spread_progress * 2 / 3
    ))
    fx.angle = (fx.angle + 2 * pi / fx.ROTATE_PERIOD) % (2 * pi)

  def update_anims(fx):
    fx.anims = [[a for a in g if not a.done] for g in fx.anims]
    fx.anims = [g for g in fx.anims if g]
    for anim_group in fx.anims:
      anim = anim_group[0]
      anim.update()
      if type(anim) is fx.AdjustAnim:
        spread_before, spread_after = anim.target
        fx.angle += (spread_after - spread_before) / fx.ADJUST_DURATION

  def view(fx):
    fx_anim = next((a for g in fx.anims for a in g if isinstance(a, FrameAnim)), None)
    fx_image = fx_anim and fx_anim.frame()
    if fx_image is None:
      return []
    return [Sprite(
      image=replace_color(fx_image, BLACK, fx.color),
      pos=fx.pos,
      origin=("center", "bottom"),
      offset=16,
      layer="elems"
    )]
