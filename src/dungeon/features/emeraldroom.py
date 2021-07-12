from dungeon.features.specialroom import SpecialRoom
from dungeon.features.room import Room
from dungeon.props.chest import Chest
from dungeon.actors.genie import Genie
from items.dungeon.emerald import Emerald
from contexts.dialogue import DialogueContext

class EmeraldRoom(SpecialRoom):
  def __init__(feature):
    super().__init__(degree=1, shape=[
      "                   ",
      "                   ",
      "                   ",
      "       .....       ",
      "      .......      ",
      "      .......      ",
      "      .......      ",
      "      .......      ",
      "      .......      ",
      "       .....       ",
      "         .         ",
      "         .         ",
      "         .         ",
    ], elems=[
      ((9, 6), Chest(Emerald)),
      ((8, 4), Genie(
        name="Joshin",
        message=lambda game: DialogueContext(script=[
          (game.talkee.get_name(), ("Well done, ", game.hero.token(), "!")),
          (game.talkee.get_name(), "You've cleared all the content for this demo."),
          (game.talkee.get_name(), "Thanks for playing, and stay tuned for more updates!"),
        ])
      ))
    ])

  def get_edges(feature):
    x, y = feature.cell or (0, 0)
    return [
      (x + 9, y - 2),
      (x + 9, y - 1),
      (x + 9, y + feature.get_height()),
      (x + 9, y + feature.get_height() + 1),
    ]
