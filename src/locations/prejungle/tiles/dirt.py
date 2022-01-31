import assets
from locations.default.tileset import Floor

class Dirt(Floor):

  @classmethod
  def render(cls, stage, cell, visited_cells):
    x, y = cell
    if (x + y) % 5:
      return assets.sprites["prejungle_dirt"]
    else:
      return assets.sprites["prejungle_dirt_cracked"]
