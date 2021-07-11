from dungeon.features.vertroom import VerticalRoom
from dungeon.features.specialroom import SpecialRoom
from dungeon.props.puzzledoor import PuzzleDoor
from dungeon.props.pushtile import PushTile
from dungeon.props.pushblock import PushBlock
from lib.cell import add as add_cell

class PuzzleRoom(SpecialRoom, VerticalRoom):
  ExitDoor = PuzzleDoor

  def __init__(room, *args, **kwargs):
    super().__init__(shape=[
      ",#.,.#,",
      ".#.....",
      ".....#.",
      ".....# ",
      "#.##...",
      "#.##. .",
      "#.### .",
    ], elems=[
      ((0, 0), PushTile()),
      ((3, 0), PushTile()),
      ((6, 0), PushTile()),
      ((2, 3), PushBlock()),
      ((5, 4), PushBlock()),
      ((6, 5), PushBlock()),
    ], *args, **kwargs)

  def get_edges(room):
    room_x, room_y = room.cell
    return [
      (room_x + 1, room_y + room.get_height()),
      (room_x + 1, room_y + room.get_height() + 1),
    ] + room.get_exits()

  def get_exits(room):
    room_x, room_y = room.cell
    return [
      (room_x + 3, room_y - 2),
      (room_x + 3, room_y - 1),
    ]
