from dungeon.features.specialroom import SpecialRoom
from dungeon.actors.skeleton import Skeleton

class ArenaRoom(SpecialRoom):
  def __init__(feature):
    feature.actors = [Skeleton()]
    super().__init__(degree=2, shape=[
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
    ], rooms=[(2, 0, 3, 4), (0, 5, 7, 7)])

  def get_edges(feature):
    x, y = feature.cell or (0, 0)
    return [(x + feature.get_width() // 2, y + feature.get_height())]
