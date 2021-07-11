from dungeon.features.room import Room
from dungeon.props.treasuredoor import TreasureDoor

class ExitRoom(Room):
  EntryDoor = TreasureDoor

  def __init__(room, secret=False):
    super().__init__((3, 4), degree=1, secret=secret)

  def place(room, stage, connectors, cell=None):
    super().place(stage, connectors, cell)
    stage.set_tile_at(room.get_center(), stage.STAIRS_UP)
