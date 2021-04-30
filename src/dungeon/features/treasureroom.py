import random
from dungeon.room import Room
from dungeon.features import Feature
from dungeon.props.chest import Chest
from skills.weapon.caladbolg import Caladbolg
from skills.weapon.longinus import Longinus
from skills.weapon.mjolnir import Mjolnir

weapons = (Caladbolg, Longinus, Mjolnir)

class TreasureRoom(Feature, Room):
  def __init__(feature):
    super().__init__()
    feature.actors = [ Chest(random.choice(weapons), rare=True) ]
    feature.rooms = [ (0, 0, 7, 7) ]
    feature.shape = [
      "#     #",
      "   0   ",
      "  ...  ",
      "  ...  ",
      "  ...  ",
      "   .   ",
      "#  .  #"
    ]

  def get_cells(feature):
    cells = super().get_cells()
    corners = {
      (0, 0),
      (0, feature.get_height() - 1),
      (feature.get_width() - 1, 0),
      (feature.get_width() - 1, feature.get_height() - 1),
    }
    return [c for c in cells if c not in corners]

  def get_edges(feature):
    x, y = feature.cell or (0, 0)
    return [(x + feature.get_width() // 2, y + feature.get_height() + 1)]
