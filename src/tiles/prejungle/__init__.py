import assets
from tiles.default import (
  Floor as DefaultFloor,
  Wall as DefaultWall
)

class Grass(DefaultFloor):
  sprite = assets.sprites["prejungle_grass"]

  @classmethod
  def render(cls, stage, cell, visited_cells):
    return assets.sprites["prejungle_grass"]


class Dirt(DefaultFloor):
  sprite = assets.sprites["prejungle_dirt"]

mappings = {
  ",": Grass,
  ".": Dirt,
}
