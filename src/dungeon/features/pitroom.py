from dungeon.features.specialroom import SpecialRoom

class PitRoom(SpecialRoom):
  def __init__(room, secret=False):
    room.shape = [
      ". . .",
      "     ",
      ". . .",
      "     ",
      ". . .",
      "     ",
      ". . ."
    ]
    super().__init__(degree=2, secret=secret)

  def get_edges(room):
    edges = super().get_edges()
    return [(x, y) for (x, y) in edges if x % 2 == 1 and y % 2 == 1]
