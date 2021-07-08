from dungeon.features.specialroom import SpecialRoom
from dungeon.props.altar import Altar
from dungeon.props.pillar import Pillar
from dungeon.actors.mage import Mage
from anims.pause import PauseAnim
from anims.jump import JumpAnim
from anims.shake import ShakeAnim
from contexts.cutscene import CutsceneContext
from contexts.dialogue import DialogueContext
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
      ((3, 5), mage := Mage(faction="ally", facing=(0, -1))),
      ((3, 4), Altar()),
      ((1, 2), Pillar()),
      ((1, 4), Pillar()),
      ((1, 6), Pillar()),
      ((5, 2), Pillar()),
      ((5, 4), Pillar()),
      ((5, 6), Pillar()),
    ], *args, **kwargs)
    room.mage = mage
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
        game.camera.focus((4, 5)),
        game.anims.append([PauseAnim(
          duration=60,
          on_end=step
        )])
      ),
      lambda step: (
        game.hero.move_to((4, 7)),
        game.anims.append([PathAnim(
          path=[(4, 11), (4, 10), (4, 9), (4, 8), (4, 7)],
          target=game.hero,
          on_end=step
        )])
      ),
      lambda step: game.anims.append([PauseAnim(
        duration=30,
        on_end=step
      )]),
      lambda step: (
        game.camera.focus((4, 7), force=True),
        game.anims.append([PauseAnim(
          duration=30,
          on_end=step
        )])
      ),
      lambda step: (
        game.anims.extend([
          [PauseAnim(duration=15)],
          [ShakeAnim(duration=15, target=room.mage)],
          [JumpAnim(target=room.mage)]
        ]),
        game.child.open(DialogueContext(
          script=[
            (game.hero.get_name(), "HEY, WOMAN!"),
            (game.hero.get_name(), "I NEED TO SEE YOUR PERMIT!"),
            CutsceneContext(script=[
              lambda step: (
                room.mage.set_facing((1, 0)),
                game.anims.append([PauseAnim(
                  duration=15,
                  on_end=step
                )])
              ),
              lambda step: (
                room.mage.set_facing((0, 1)),
                game.anims.append([PauseAnim(
                  duration=15,
                  on_end=step
                )])
              ),
            ]),
            (room.mage.get_name(), "The hell?"),
          ],
          on_close=step
        ))
      )
    ]))
