from dungeon.features.vertroom import VerticalRoom
from dungeon.features.specialroom import SpecialRoom
from dungeon.props.puzzledoor import PuzzleDoor
from dungeon.props.pushtile import PushTile
from dungeon.props.pushblock import PushBlock
from lib.cell import add as add_cell

class PushBlockRoom(SpecialRoom, VerticalRoom):
  ExitDoor = PuzzleDoor

  def __init__(room, *args, **kwargs):
    super().__init__(shape=[
      ".....",
      ".....",
      "...,.",
      ".....",
    ], elems=[
      ((3, 2), PushTile()),
      ((1, 2), PushBlock()),
    ], *args, **kwargs)

  def get_edges(room):
    room_x, room_y = room.cell
    return [(x, y) for (x, y) in super().get_edges() if y >= room_y + room.get_height()]

  def place(room, stage, cell=None, connectors=[]):
    if not super().place(stage, cell=None, connectors=[]):
      return False
    pushtile_cell = add_cell(connectors[1], (0, 1))
    stage.set_tile_at(pushtile_cell, stage.DOOR_WAY)
    stage.spawn_elem_at(pushtile_cell, PushTile())
    return True
