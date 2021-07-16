from dungeon.features.room import Room

class ExitRoom(Room):
  def __init__(room, size=(3, 4), secret=False, *args, **kwargs):
    super().__init__(degree=1, size=size, secret=secret, *args, **kwargs)

  def place(room, stage, *args, **kwargs):
    if not super().place(stage, *args, **kwargs):
      return False
    stage.set_tile_at(room.get_center(), stage.STAIRS_UP)
    return True
