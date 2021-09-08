from random import randint
from pygame.transform import rotate
from dungeon.props import Prop
import assets
from filters import replace_color
from sprite import Sprite
from config import TILE_SIZE
from colors.palette import WHITE, COLOR_TILE

class VCoffin(Prop):
  static = True
  solid = False
  image = rotate(assets.sprites["coffin_lid"], -90)
  image = replace_color(image, WHITE, COLOR_TILE)

  def view(coffin, *args, **kwargs):
    return super().view([Sprite(
      image=coffin.image,
      pos=(0, -16),
      offset=16,
      layer="elems"
    )], *args, **kwargs)
