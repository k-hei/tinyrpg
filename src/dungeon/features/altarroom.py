from dungeon.features.specialroom import SpecialRoom
from dungeon.floors.floor1 import Floor1
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
from transits.dissolve import DissolveIn, DissolveOut
from lib.cell import add
import config
from config import RUN_DURATION

class AltarRoom(SpecialRoom):
  def __init__(room, *args, **kwargs):
    super().__init__(degree=2, shape=[
      "         ",
      "         ",
      "  .....  ",
      " ....... ",
      " ....... ",
      " ....... ",
      " ....... ",
      " ....... ",
      "  .....  ",
      "    .    ",
      "    .    ",
      "    .    ",
      "    .    ",
      "    .    ",
    ], elems=[
      ((4, 6), mage := Mage(faction="ally", facing=(0, -1))),
      ((4, 5), altar := Altar()),
      ((2, 7), Pillar()),
      ((1, 6), Pillar()),
      ((1, 4), Pillar()),
      ((1, 2), Pillar()),
      ((2, 1), Pillar()),
      ((6, 1), Pillar()),
      ((7, 2), Pillar()),
      ((7, 4), Pillar()),
      ((7, 6), Pillar()),
      ((6, 7), Pillar()),
    ], *args, **kwargs)
    room.mage = mage
    room.altar = altar
    room.entered = False

  def get_edges(room):
    room_width, room_height = room.get_size()
    room_x, room_y = room.cell or (0, 0)
    return [
      (room_x + room_width // 2, room_y + room_height)
    ]

  def on_enter(room, game):
    game.open(CutsceneContext(script=[
      *(cutscene(room, game) if config.CUTSCENES else []),
      lambda step: (
        game.get_head().transition(
          transits=(DissolveIn(), DissolveOut()),
          loader=Floor1(),
          on_end=lambda floor: (
            game.use_floor(floor, loader=Floor1),
            step()
          )
        )
      )
    ]))

def cutscene(room, game):
  return [
    lambda step: (
      game.camera.focus(cell=room.altar.cell, speed=90, tween=True),
      game.anims.append([PauseAnim(
        duration=60,
        on_end=step
      )])
    ),
    lambda step: (
      game.hero.move_to(add(room.cell, (4, 7))),
      game.anims.append([PathAnim(
        target=game.hero,
        path=[add(room.cell, c) for c in [(4, 13), (4, 12), (4, 11), (4, 10), (4, 9), (4, 8), (4, 7)]],
        on_end=step
      )])
    ),
    lambda step: game.anims.append([PauseAnim(duration=30, on_end=step)]),
    lambda step: (
      game.camera.focus(
        cell=add(room.cell, (4, 7)),
        speed=60,
        tween=True,
        on_end=step
      )
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
              game.anims.append([PauseAnim(duration=15, on_end=step)])
            ),
            lambda step: (
              room.mage.set_facing((0, 1)),
              game.anims.append([PauseAnim(duration=15, on_end=step)])
            ),
          ]),
          (room.mage.get_name(), "The hell?"),
          CutsceneContext(script=[
            lambda step: (
              game.camera.focus(
                cell=add(room.cell, (4, 5)),
                speed=30,
                tween=True
              ),
              room.mage.move_to(add(room.cell, (3, 4))),
              game.anims.append([PathAnim(
                target=room.mage,
                path=[add(room.cell, c) for c in [(4, 6), (3, 6), (3, 5), (3, 4)]],
                period=RUN_DURATION,
                on_end=step
              )])
            ),
            lambda step: (
              room.mage.set_facing((0, 1)),
              game.hero.move_to(add(room.cell, (4, 6))),
              game.anims.append([PathAnim(
                target=game.hero,
                path=[add(room.cell, c) for c in [(4, 7), (4, 6)]],
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
      game.floor.set_tile_at(add(room.cell, cell), game.floor.PIT),
      game.redraw_tiles(force=True),
      game.anims.append([PauseAnim(duration=5, on_end=step)]),
    ))(c) for c in [(3, 3), (4, 3), (5, 3), (5, 4), (5, 5), (5, 6), (4, 6), (3, 6), (3, 5), (3, 4)]],
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
    )
  ]
