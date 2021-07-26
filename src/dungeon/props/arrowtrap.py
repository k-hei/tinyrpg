from pygame.transform import flip
from dungeon.props import Prop
from anims import Anim
from sprite import Sprite
import assets
from colors.palette import WHITE, SAFFRON
from filters import replace_color

ARROW_PERIOD = 300

class ArrowTrap(Prop):
  def __init__(trap, facing, *args, **kwargs):
    super().__init__(*args, **kwargs)
    trap.facing = facing
    trap.anim = Anim(duration=ARROW_PERIOD)

  def surface(trap):
    if trap.facing == (-1, 0):
      surface = flip(assets.sprites["arrowtrap_right"], True, False)
    elif trap.facing == (1, 0):
      surface = assets.sprites["arrowtrap_right"]
    else:
      surface = assets.sprites["arrowtrap_down"]
    surface = replace_color(surface, WHITE, SAFFRON)
    return surface

  def update(trap):
    trap.anim.update()
    if trap.anim.done:
      trap.anim = Anim(duration=ARROW_PERIOD)
    else:
      trap.anim.update()

  def view(trap, anims):
    return super().view(Sprite(
      image=trap.surface(),
      layer="elems"
    ), anims)
