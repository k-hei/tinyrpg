from cores import Core
from sprite import Sprite
import assets

class Radhead(Core):
  def view(bughead):
    bughead_image = assets.sprites["radhead"]
    flip_x = bughead.facing == (-1, 0)
    return super().view([Sprite(
      image=bughead_image,
      flip=(flip_x, False),
      layer="elems"
    )])
