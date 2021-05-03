from config import MOVE_DURATION
from town.actors import Actor
from assets import load as use_assets
from filters import replace_color
from palette import BLACK, BLUE

class Knight(Actor):
  def __init__(knight, core):
    super().__init__(core)

  def render(knight):
    sprites = use_assets().sprites
    image = sprites["knight"]
    if knight.walks:
      if knight.walks % (MOVE_DURATION // 2) < MOVE_DURATION // 4:
        image = sprites["knight_walk"]
    image = replace_color(image, BLACK, BLUE)
    knight.sprite.image = image
    return super().render()
