from pygame.transform import rotate
from dungeon.props import Prop
import assets
from lib.filters import replace_color
from lib.sprite import Sprite
from colors.palette import WHITE

class VCoffin(Prop):
  static = True
  solid = False
  image = rotate(assets.sprites["coffin_lid"], -90)

  def view(coffin, *args, **kwargs):
    return super().view([Sprite(
      image=replace_color(coffin.image, WHITE, coffin.color),
      pos=(0, -24),
      layer="elems"
    )], *args, **kwargs)
