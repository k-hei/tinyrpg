from lib.sprite import Sprite
from cores import Core
import assets
from config import BOAR_NAME

class Boar(Core):
  name = BOAR_NAME

  def __init__(boar, *args, **kwargs):
    super().__init__(name=Boar.name, *args, **kwargs)

  def view(boar):
    return super().view([Sprite(
      image=assets.sprites["boar"],
      flip=(boar.facing == (-1, 0), False),
      layer="elems"
    )])
