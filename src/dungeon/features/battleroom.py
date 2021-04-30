from dungeon.features.specialroom import SpecialRoom
from dungeon.actors.eye import Eye
from dungeon.actors.mushroom import Mushroom

class BattleRoom(SpecialRoom):
  def __init__(feature):
    feature.actors = (Mushroom(), Eye(), Mushroom())
    feature.actors[1].inflict_ailment("sleep")
    feature.actors[2].inflict_ailment("sleep")
    feature.shape = [
      "....2..",
      ".   .1.",
      ".   ...",
      ".0.....",
      "...   .",
      "...   .",
      "......."
    ]
    super().__init__()
    feature.degree = 2

  def get_edges(feature):
    x, y = feature.cell or (0, 0)
    return [
      (x + feature.get_width() // 2, y - 1),
      (x + feature.get_width() // 2, y + feature.get_height() + 1),
      (x - 1, y + feature.get_height() // 2),
      (x + feature.get_width(), y + feature.get_height() // 2)
    ]
