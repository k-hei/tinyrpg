from town.areas import Area, AreaLink
from config import TILE_SIZE

class ClearingArea(Area):
  bg_id = "town_clearing"

  def render(area, hero):
    nodes = super().render(hero)
    for i, sprite in enumerate(nodes):
      if i == 0:
        continue
      x, y = sprite.pos
      sprite.pos = (x, y - TILE_SIZE // 4)
    return nodes
