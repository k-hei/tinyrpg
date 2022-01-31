from random import choice
from lib.sprite import Sprite
import assets
from dungeon.element import DungeonElement as Element

class PrejungleGrass(Element):
  def __init__(grass, *args, **kwargs):
    super().__init__(*args, **kwargs)
    grass.kind = choice(("s", "l"))

  def view(grass, *args, **kwargs):
    return super().view([Sprite(
      image=assets.sprites[f"prejungle_grass_{grass.kind}"],
      layer="elems",
    )], *args, **kwargs)
