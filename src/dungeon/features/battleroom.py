import random
from dungeon.features import Feature
from actors.eye import Eye
from actors.skeleton import Skeleton

class BattleRoom(Feature):
  def __init__(feature):
    super().__init__()
    feature.actors = (Skeleton(), Eye(), Skeleton())
    feature.actors[1].inflict("sleep")
    feature.actors[2].inflict("sleep")
    feature.rooms = ((2, 0, 3, 3), (0, 5, 7, 5))
    feature.shape = [
      "##...##",
      "##.<.##",
      "##...##",
      "###.###",
      "###+###"
    ]
    if random.randint(1, 2) == 1:
      feature.shape.extend([
        "....2..",
        ".  ..1.",
        ".  .  .",
        ".0..  .",
        "......."
      ])
    else:
      feature.shape.extend([
        ".2.....",
        "..1.  .",
        ".  .  .",
        ".  ..0.",
        "......."
      ])

  def get_edges(feature):
    x, y = feature.cell or (0, 0)
    return [(x + 3, y + feature.get_height() + 1)]
