import config
from assets import load as use_assets
from actors.town import Actor

class Mage(Actor):
  def __init__(mage):
    super().__init__()

  def render(mage):
    sprites = use_assets().sprites
    sprite = sprites["mage"]
    if mage.walks:
      if mage.walks % (config.MOVE_DURATION // 2) < config.MOVE_DURATION // 4:
        sprite = sprites["mage_walk"]
    return super().render(sprite)
