from dungeon.features.specialroom import SpecialRoom
from dungeon.props.altar import Altar
from dungeon.props.pillar import Pillar
from contexts.cutscene import CutsceneContext
from anims.path import PathAnim

class AltarRoom(SpecialRoom):
  def __init__(room, *args, **kwargs):
    super().__init__(degree=2, shape=[
      ".......",
      "       ",
      " ..... ",
      " ..... ",
      " ..... ",
      " ..... ",
      " ..... ",
      "   .   ",
      "   .   ",
      "   .   ",
      "   .   ",
    ], elems=[
      ((3, 4), Altar()),
      ((1, 2), Pillar()),
      ((1, 4), Pillar()),
      ((1, 6), Pillar()),
      ((5, 2), Pillar()),
      ((5, 4), Pillar()),
      ((5, 6), Pillar()),
    ], *args, **kwargs)
    room.entered = False

  def get_edges(room):
    room_width, room_height = room.get_size()
    room_x, room_y = room.cell or (0, 0)
    return [
      (room_x + room_width // 2, room_y + room.get_height())
    ]

  def on_enter(room, game):
    game.open(CutsceneContext(script=lambda game: [
      lambda step: (
        game.hero.move_to((4, 6)),
        game.anims.append([PathAnim(
          path=[(4, 11), (4, 10), (4, 9), (4, 8), (4, 7), (4, 6), (3, 6), (3, 5), (3, 4), (4, 4), (5, 4), (5, 5), (5, 6), (4, 6)],
          target=game.hero,
          on_end=step
        )])
      )
    ]))
