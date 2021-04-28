import random
from dungeon.features import Feature
from dungeon.actors.eye import Eye
from dungeon.actors.mushroom import Mushroom

configs = (
  [
    "....2..",
    ".  ..1.",
    ".  .  .",
    ".0..  .",
    "......."
  ],
  [
    ".2.....",
    "..1.  .",
    ".  .  .",
    ".  ..0.",
    "......."
  ]
)

class BattleRoom(Feature):
  def __init__(feature):
    super().__init__()
    feature.actors = (Mushroom(), Eye(), Mushroom())
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
    feature.shape.extend(random.choice(configs))

  def get_edges(feature):
    x, y = feature.cell or (0, 0)
    return [(x + 3, y + feature.get_height() + 1)]
