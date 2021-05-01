from dungeon.features.specialroom import SpecialRoom

class CoffinRoom(SpecialRoom):
  def __init__(room, secret=False):
    room.shape = [
      ".....",
      ".=.=.",
      ".....",
      ".=.=.",
      ".....",
      ".=.=.",
      "....."
    ]
    super().__init__(secret=secret)
