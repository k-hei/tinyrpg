from cores import Core
from lib.sprite import Sprite
from assets import load as use_assets

class Rat(Core):
  def view(rat):
    rat_image = use_assets().sprites["rat"]
    flip_x = rat.facing == (-1, 0)
    return super().view([Sprite(
      image=rat_image,
      flip=(flip_x, False),
      pos=(0, 0),
      layer="elems"
    )])
