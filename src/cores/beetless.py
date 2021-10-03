from cores import Core
from lib.sprite import Sprite
import assets

class Beetless(Core):
  def view(bughead):
    bughead_image = assets.sprites["beetless"]
    flip_x = bughead.facing == (-1, 0)
    return super().view([Sprite(
      image=bughead_image,
      flip=(flip_x, False),
      layer="elems"
    )])
