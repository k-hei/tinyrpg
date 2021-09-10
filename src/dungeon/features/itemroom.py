from random import choice
from lib.cell import manhattan, neighborhood
from dungeon.features.room import Room
from dungeon.props.chest import Chest
from dungeon.gen import gen_elems

class ItemRoom(Room):
  def __init__(room, items=[], *args, **kwargs):
    super().__init__(degree=1, *args, **kwargs)
    room.items = items

  def place(room, stage, cell=None, connectors=[]):
    if not super().place(stage, cell, connectors):
      return False
    gen_elems(stage, room,
      elems=[Chest(Item) for Item in room.items],
      doors=connectors)
    return True
