import config
from assets import load as use_assets
from actors.town import Actor

class Knight(Actor):
  def __init__(knight):
    super().__init__()

  def render(knight):
    sprites = use_assets().sprites
    sprite = sprites["knight"]
    if knight.walks:
      if knight.walks % (config.MOVE_DURATION // 2) < config.MOVE_DURATION // 4:
        sprite = sprites["knight_walk"]
    return super().render(sprite)
