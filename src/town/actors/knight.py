import config
from town.actors import Actor
from assets import load as use_assets
from filters import replace_color
import palette

class Knight(Actor):
  def __init__(knight):
    super().__init__()

  def render(knight):
    sprites = use_assets().sprites
    sprite = sprites["knight"]
    if knight.walks:
      if knight.walks % (config.MOVE_DURATION // 2) < config.MOVE_DURATION // 4:
        sprite = sprites["knight_walk"]
    sprite = replace_color(sprite, palette.BLACK, palette.BLUE)
    return super().render(sprite)
