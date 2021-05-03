from config import MOVE_DURATION
from town.actors import Actor
from assets import load as use_assets
from filters import replace_color
from palette import BLACK, BLUE

class Mage(Actor):
  def __init__(mage, core):
    super().__init__(core)

  def render(mage):
    sprites = use_assets().sprites
    image = sprites["mage"]
    if mage.walks:
      if mage.walks % (MOVE_DURATION // 2) < MOVE_DURATION // 4:
        image = sprites["mage_walk"]
    image = replace_color(image, BLACK, BLUE)
    mage.sprite.image = image
    return super().render()
