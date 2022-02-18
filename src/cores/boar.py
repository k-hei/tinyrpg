from lib.sprite import Sprite
from cores import Core
import assets
from config import BOAR_NAME

class Boar(Core):
  name = BOAR_NAME

  def __init__(boar, *args, **kwargs):
    super().__init__(name=Boar.name, *args, **kwargs)

  def view(boar):
    boar_image = assets.sprites["boar"]
    flip_x = boar.facing == (-1, 0)
    return super().view([Sprite(
      image=boar_image,
      flip=(flip_x, False),
      pos=(0, 0),
      layer="elems"
    )])
