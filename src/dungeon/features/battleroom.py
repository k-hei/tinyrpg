from dungeon.features.specialroom import SpecialRoom
from dungeon.actors.eyeball import Eyeball
from dungeon.actors.mushroom import Mushroom
from random import choice

class BattleRoom(SpecialRoom):
  def __init__(feature, *args, **kwargs):
    feature.actors = (Mushroom(), Eyeball(), Mushroom())
    feature.actors[1].inflict_ailment("sleep")
    feature.actors[2].inflict_ailment("sleep")
    super().__init__(degree=2, shape=choice(([
      "....2..",
      ".   .1.",
      ".   ...",
      ".0.....",
      "...   .",
      "...   .",
      "......."
    ], [
      ".....1.",
      "2..   .",
      "...   .",
      ".......",
      ".   0..",
      ".   ...",
      "......."
    ], [
      ".......",
      ".  .  .",
      ". 0.. .",
      "....1..",
      ". ... .",
      ".  .  .",
      ".2....."
    ])), *args, **kwargs)

  def get_edges(feature):
    x, y = feature.cell or (0, 0)
    return [
      (x + feature.get_width() // 2, y - 2),
      (x + feature.get_width() // 2, y - 1),
      (x + feature.get_width() // 2, y + feature.get_height()),
      (x + feature.get_width() // 2, y + feature.get_height() + 1),
      (x - 1, y + feature.get_height() // 2),
      (x + feature.get_width(), y + feature.get_height() // 2)
    ]
