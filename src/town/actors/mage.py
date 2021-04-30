import config
from town.actors import Actor
from assets import load as use_assets
from filters import replace_color
import palette

class Mage(Actor):
  def __init__(mage, core):
    super().__init__(core)

  def render(mage):
    sprites = use_assets().sprites
    sprite = sprites["mage"]
    if mage.walks:
      if mage.walks % (config.MOVE_DURATION // 2) < config.MOVE_DURATION // 4:
        sprite = sprites["mage_walk"]
    sprite = replace_color(sprite, palette.BLACK, palette.BLUE)
    return super().render(sprite)
