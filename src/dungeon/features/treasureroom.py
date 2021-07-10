from dungeon.features.specialroom import SpecialRoom
from dungeon.props.chest import Chest

class TreasureRoom(SpecialRoom):
  def __init__(room, item):
    super().__init__(degree=1, secret=True, shape=[
      "...",
      "...",
      "...",
      "...",
    ], elems=[
      ((1, 1), Chest(item))
    ])
