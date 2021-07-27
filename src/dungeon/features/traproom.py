from dungeon.features.specialroom import SpecialRoom
from dungeon.props.arrowtrap import ArrowTrap
from dungeon.props.bag import Bag
from skills.armor.buckler import Buckler

class TrapRoom(SpecialRoom):
  def __init__(room, *args, **kwargs):
    super().__init__(shape=[
      ".....",
      ".....",
      ".....",
      ".....",
    ], elems=[
      ((0, 1), ArrowTrap(facing=(1, 0))),
      ((2, 0), ArrowTrap(facing=(0, 1))),
      ((4, 2), ArrowTrap(facing=(-1, 0))),
      ((0, 3), Bag(Buckler))
    ], *args, **kwargs)
