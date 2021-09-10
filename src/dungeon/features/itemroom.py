from random import choice
from lib.cell import manhattan, neighborhood
from dungeon.features.room import Room
from dungeon.props.chest import Chest
from dungeon.gen import gen_items

class ItemRoom(Room):
  def __init__(room, items=[], *args, **kwargs):
    super().__init__(degree=1, *args, **kwargs)
    room.items = items

  def place(room, stage, cell=None, connectors=[]):
    if not super().place(stage, cell, connectors):
      return False
    gen_items(stage, room, room.items, connectors)
    return True
