from dungeon.features.room import Room

class ExitRoom(Room):
  def __init__(room, secret=False):
    super().__init__((3, 4), degree=1, secret=secret)

  def place(room, stage):
    super().place(stage)
    stage.set_tile_at(room.get_center(), stage.STAIRS_UP)
