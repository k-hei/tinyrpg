import lib.vector as vector
from dungeon.features.specialroom import SpecialRoom
from dungeon.props.arrowtrap import ArrowTrap
from dungeon.props.chest import Chest
from dungeon.actors.eye import Eyeball
from items.sp.fish import Fish

class TrapRoom(SpecialRoom):
  def __init__(room, *args, **kwargs):
    super().__init__(shape=[
      "     .../··",
      "      ...··",
      ".....  ..··",
      "..  .  ..··",
      "..  .....··",
      "   ..  ....",
      "   ..      ",
    ], elems=[
      ((0, 0), ArrowTrap(facing=(1, 0))),
      ((8, 4), ArrowTrap(facing=(-1, 0))),
      ((3, 5), Eyeball()),
      ((10, 5), Chest(Fish))
    ], *args, **kwargs)

  def get_entrances(room):
    return [
      vector.add(room.cell, (-1, 2)),
      vector.add(room.cell, (-1, 3)),
      vector.add(room.cell, (-1, 4)),
    ]

  def get_exits(room):
    return [
      vector.add(room.cell, (5, -1)),
    ]
