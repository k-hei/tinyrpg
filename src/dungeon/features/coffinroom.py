from random import randint, choice
from dungeon.features.specialroom import SpecialRoom
from dungeon.props.coffin import Coffin
from dungeon.props.vcoffin import VCoffin
from items.gold import Gold
from config import ROOM_WIDTHS, ROOM_HEIGHTS
import lib.vector as vector

class CoffinRoom(SpecialRoom):
  def __init__(room, *args, **kwargs):
    super().__init__(
      shape=["." * 9 for _ in range(7)],
      elems=[
        ((1, 0), VCoffin()),
        ((3, 0), VCoffin()),
        ((5, 0), VCoffin()),
        ((7, 0), VCoffin()),
        ((2, 2), Coffin()),
        ((4, 2), Coffin()),
        ((6, 2), Coffin()),
        ((2, 4), Coffin()),
        ((4, 4), Coffin()),
        ((6, 4), Coffin()),
      ],
      *args, **kwargs
    )

  def get_edges(room):
    return [
      vector.add(room.cell, (room.get_width() // 2, room.get_height()))
    ]
