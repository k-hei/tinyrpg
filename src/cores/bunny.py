from lib.sprite import Sprite
from cores import Core
import assets
from config import BUNNY_NAME

class Bunny(Core):
  name = BUNNY_NAME

  def __init__(bunny, *args, **kwargs):
    super().__init__(name=Bunny.name, *args, **kwargs)

  def view(bunny):
    return super().view([Sprite(
      image=assets.sprites["bunny"],
      flip=(bunny.facing == (-1, 0), False),
      layer="elems"
    )])
