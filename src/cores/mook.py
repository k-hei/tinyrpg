from lib.sprite import Sprite
from cores import Core
import assets

class Mook(Core):
  def view(mook):
    mook_image = assets.sprites["mook"]
    if mook.facing == (0, 1):
      mook_image = assets.sprites["mook_down"]
    return super().view([Sprite(
      image=mook_image,
      flip=(mook.facing == (-1, 0), False),
      layer="elems"
    )])
