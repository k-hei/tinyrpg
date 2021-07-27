from dungeon.features.specialroom import SpecialRoom
from dungeon.props.arrowtrap import ArrowTrap
from dungeon.props.bag import Bag
from skills.armor.buckler import Buckler
import lib.vector as vector

class GauntletRoom(SpecialRoom):
  def __init__(room, *args, **kwargs):
    super().__init__(shape=[
      "             ....",
      "...    .    .....",
      ".....  ..........",
      "......   .   ....",
      "...  .....   ....",
      "...    .     ....",
      "             ....",
    ], elems=[
      ((16, 2), ArrowTrap(facing=(-1, 0), delay=100)),
      ((16, 4), ArrowTrap(facing=(-1, 0))),
      ((5, 0), ArrowTrap(facing=(0, 1), delay=45)),
      ((8, 0), ArrowTrap(facing=(0, 1), delay=60)),
      ((11, 0), ArrowTrap(facing=(0, 1), delay=75)),
      ((0, 3), Bag(Buckler))
    ], *args, **kwargs)

  def get_edges(room):
    return [
      vector.add(room.cell, (-1, 1)),
      vector.add(room.cell, (-1, 2)),
      vector.add(room.cell, (-1, 3)),
      vector.add(room.cell, (-1, 4)),
      vector.add(room.cell, (-1, 5)),
    ]
