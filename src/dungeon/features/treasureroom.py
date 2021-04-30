import random
from dungeon.features.room import Room
from dungeon.props.chest import Chest
from skills.weapon.caladbolg import Caladbolg
from skills.weapon.longinus import Longinus
from skills.weapon.mjolnir import Mjolnir

weapons = (Caladbolg, Longinus, Mjolnir)

class TreasureRoom(Room):
  def __init__(room):
    super().__init__()
    room.actors = [ Chest(random.choice(weapons), rare=True) ]
    room.shape = [
      "#     #",
      "   0   ",
      "  ...  ",
      "  ...  ",
      "  ...  ",
      "   .   ",
      "#  .  #"
    ]

  def get_cells(room):
    cells = super().get_cells()
    corners = {
      (0, 0),
      (0, room.get_height() - 1),
      (room.get_width() - 1, 0),
      (room.get_width() - 1, room.get_height() - 1),
    }
    return [c for c in cells if c not in corners]

  def get_edges(room):
    x, y = room.cell or (0, 0)
    return [(x + room.get_width() // 2, y + room.get_height() + 1)]
