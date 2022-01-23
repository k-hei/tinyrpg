from pygame import Rect
from pygame.transform import flip
import lib.vector as vector
from lib.sprite import Sprite
from lib.filters import replace_color
from colors.palette import WHITE, SAFFRON

from dungeon.props import Prop
from vfx.arrow import Arrow
from anims import Anim
import assets
from config import TILE_SIZE

ARROW_PERIOD = 300

class ArrowTrap(Prop):
  solid = True
  active = False

  def __init__(trap, facing, delay=0, static=True, *args, **kwargs):
    super().__init__(static=static, *args, **kwargs)
    trap.facing = facing
    trap.delay = delay
    trap.anim = Anim(duration=trap.delay or ARROW_PERIOD, delay=trap.delay)

  @property
  def rect(trap):
    if trap._rect is None and trap.pos:
      if trap.facing == (0, 1):
        trap._rect = Rect(
          vector.add(trap.pos, (-8, -14)),
          (18, 12)
        )
      elif trap.facing == (1, 0):
        trap._rect = Rect(
          vector.add(trap.pos, (-16, -8)),
          (12, 18)
        )
      elif trap.facing == (-1, 0):
        trap._rect = Rect(
          vector.add(trap.pos, (4, -8)),
          (12, 18)
        )
    return trap._rect

  def surface(trap):
    if trap.facing == (-1, 0):
      surface = flip(assets.sprites["arrowtrap_right"], True, False)
    elif trap.facing == (1, 0):
      surface = assets.sprites["arrowtrap_right"]
    else:
      surface = assets.sprites["arrowtrap_down"]
    surface = replace_color(surface, WHITE, SAFFRON)
    return surface

  def update(trap, game):
    pass
    # if not game.room or trap.cell not in game.room.get_cells():
    #   return
    # trap.anim.update()
    # if trap.anim.done:
    #   trap.anim = Anim(duration=ARROW_PERIOD)
    #   return [Arrow(
    #     cell=trap.cell,
    #     direction=trap.facing
    #   )]
    # else:
    #   trap.anim.update()

  def view(trap, anims):
    trap_image = trap.surface()
    return super().view([Sprite(
      image=trap_image,
      origin=("center", "bottom"),
      layer="elems"
    )], anims)
