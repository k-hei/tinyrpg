from pygame import Surface, SRCALPHA
import assets
from lib.filters import replace_color
from colors.palette import WHITE, GRAY, GOLD

class Rarity:
  def render(rarity):
    empty_star = replace_color(assets.sprites["rarity_star"], WHITE, GRAY)
    filled_star = replace_color(assets.sprites["rarity_star"], WHITE, GOLD)
    rarity_surface = Surface((empty_star.get_width() * 3, empty_star.get_height()), flags=SRCALPHA)
    for i in range(3):
      rarity_surface.blit(filled_star if i < rarity else empty_star, (i * empty_star.get_width(), 0))
    return rarity_surface
