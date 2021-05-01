from config import MOVE_DURATION
from town.actors import Actor
from assets import load as use_assets
from filters import replace_color
import palette

class Knight(Actor):
  def __init__(knight, core):
    super().__init__(core)

  def render(knight):
    sprites = use_assets().sprites
    sprite = sprites["knight"]
    if knight.walks:
      if knight.walks % (MOVE_DURATION // 2) < MOVE_DURATION // 4:
        sprite = sprites["knight_walk"]
    sprite = replace_color(sprite, palette.BLACK, palette.BLUE)
    return super().render(sprite)
