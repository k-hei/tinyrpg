from lib.sprite import Sprite
from cores import Core
import assets
from config import MOUSE_NAME

class Mouse(Core):
  name = MOUSE_NAME

  def __init__(mouse, *args, **kwargs):
    super().__init__(name=Mouse.name, *args, **kwargs)

  def view(mouse):
    mouse_image = assets.sprites["mouse"]
    flip_x = mouse.facing == (-1, 0)
    return super().view([Sprite(
      image=mouse_image,
      flip=(flip_x, False),
      pos=(0, 0),
      layer="elems"
    )])
