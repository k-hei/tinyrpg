from dungeon.features.specialroom import SpecialRoom
from dungeon.props.altar import Altar
from dungeon.props.pillar import Pillar
from dungeon.actors.mage import Mage
from anims.pause import PauseAnim
from anims.jump import JumpAnim
from anims.shake import ShakeAnim
from anims.path import PathAnim
from anims.flicker import FlickerAnim
from contexts.cutscene import CutsceneContext
from contexts.dialogue import DialogueContext
from config import RUN_DURATION
from transits.dissolve import DissolveIn, DissolveOut

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
      " ..... ",
      "   .   ",
      "   .   ",
      "   .   ",
      "   .   ",
      "   .   ",
      "   .   ",
    ], elems=[
      ((3, 6), mage := Mage(faction="ally", facing=(0, -1))),
      ((3, 5), Altar()),
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
        game.camera.focus((4, 6)),
        game.anims.append([PauseAnim(
          duration=60,
          on_end=step
        )])
      ),
      lambda step: (
        game.hero.move_to((4, 8)),
        game.anims.append([PathAnim(
          target=game.hero,
          path=[(4, 14), (4, 13), (4, 12), (4, 11), (4, 10), (4, 9), (4, 8)],
          period=RUN_DURATION,
          on_end=step
        )])
      ),
      lambda step: game.anims.append([PauseAnim(
        duration=30,
        on_end=step
      )]),
      lambda step: (
        game.camera.focus((4, 8), force=True),
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
            CutsceneContext(script=[
              lambda step: (
                game.camera.focus((4, 6), force=True),
                room.mage.move_to((3, 5)),
                game.anims.append([PathAnim(
                  target=room.mage,
                  path=[(4, 7), (3, 7), (3, 6), (3, 5)],
                  period=RUN_DURATION,
                  on_end=step
                )])
              ),
              lambda step: (
                room.mage.set_facing((0, 1)),
                game.hero.move_to((4, 7)),
                game.anims.append([PathAnim(
                  target=game.hero,
                  path=[(4, 8), (4, 7)],
                  period=RUN_DURATION
                )]),
                step()
              )
            ]),
            (room.mage.get_name(), "Stay away from me, you freak!"),
            (game.hero.get_name(), "YOU'RE NOT GETTING AWAY!"),
          ],
          on_close=step
        ))
      ),
      *[(lambda cell: lambda step: (
        game.floor.set_tile_at(cell, game.floor.PIT),
        game.redraw_tiles(),
        game.anims.append([PauseAnim(duration=5, on_end=step)]),
      ))(c) for c in [(3, 4), (4, 4), (5, 4), (5, 5), (5, 6), (5, 7), (4, 7), (3, 7), (3, 6), (3, 5)]],
      lambda step: game.anims.append([PauseAnim(duration=30, on_end=step)]),
      lambda step: (
        game.anims.extend([
          [
            ShakeAnim(
              target=game.hero,
              duration=30
            ),
            ShakeAnim(
              target=room.mage,
              duration=30
            )
          ],
          [
            FlickerAnim(
              target=game.hero,
              duration=30,
              on_end=lambda: game.floor.remove_elem(game.hero)
            ),
            FlickerAnim(
              target=room.mage,
              duration=30,
              on_end=lambda: game.floor.remove_elem(room.mage)
            )
          ],
          [PauseAnim(
            duration=15,
            on_end=step
          )]
        ])
      ),
      lambda step: (
        game.get_root().transition(
          DissolveIn(),
          DissolveOut(on_end=step)
        )
      )
    ]))
