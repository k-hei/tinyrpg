from random import choice
from config import ROOM_WIDTHS, ROOM_HEIGHTS
from dungeon.features.room import Room
from dungeon.props.coffin import Coffin

class CoffinRoom(Room):
  def __init__(room, *args, **kwargs):
    width = choice([w for w in ROOM_WIDTHS if w % 2 == 1])
    height = choice([h for h in ROOM_HEIGHTS if h % 2 == 1])
    super().__init__((width, height), *args, **kwargs)

  def place(room, stage):
    super().place(stage)
    room_width, room_height = room.get_size()
    room_x, room_y = room.cell or (0, 0)
    for y in range(room_height):
      for x in range(room_width):
        col, row = (room_x + x, room_y + y)
        cell = (col, row)
        stage.set_tile_at(cell, stage.FLOOR)
        if x % 2 == 1 and y % 2 == 1:
          stage.spawn_elem(Coffin(), cell)
