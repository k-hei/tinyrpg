import random
from dungeon.features import Feature
from actors.skeleton import Skeleton

class BattleRoom(Feature):
  def __init__(feature):
    super().__init__()
    feature.actors = (Skeleton(),)
    feature.rooms = ((2, 0, 3, 4), (0, 5, 7, 7))
    feature.shape = [
      "##...##",
      "##.<.##",
      "##...##",
      "##...##",
      "###.###",
      "###+###",
      "#  0  #",
      "   .   ",
      "  ...  ",
      "  ...  ",
      "  ...  ",
      "   .   ",
      "#  .  #"
    ]

  def get_edges(feature):
    x, y = feature.cell or (0, 0)
    return [(x + feature.get_width() // 2, y + feature.get_height() + 1)]
