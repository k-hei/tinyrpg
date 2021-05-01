from dungeon.features.room import Room

class ExitRoom(Room):
  def __init__(room, secret=False):
    super().__init__((3, 4), degree=1, secret=secret)
