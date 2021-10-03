from pygame.transform import flip
from dungeon.props import Prop
from vfx.arrow import Arrow
from anims import Anim
from sprite import Sprite
import assets
from lib.filters import replace_color
from colors.palette import WHITE, SAFFRON
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
    if not game.room or trap.cell not in game.room.get_cells():
      return
    trap.anim.update()
    if trap.anim.done:
      trap.anim = Anim(duration=ARROW_PERIOD)
      return [Arrow(
        cell=trap.cell,
        direction=trap.facing
      )]
    else:
      trap.anim.update()

  def view(trap, anims):
    trap_image = trap.surface()
    return super().view([Sprite(
      image=trap_image,
      origin=("left", "bottom"),
      layer="elems"
    )], anims)
