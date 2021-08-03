from dungeon.features.specialroom import SpecialRoom
from dungeon.floors.floor1 import Floor1
from dungeon.props.altar import Altar
from dungeon.props.pillar import Pillar
from dungeon.actors.mage import Mage
from anims.pause import PauseAnim
from anims.jump import JumpAnim
from anims.shake import ShakeAnim
from anims.path import PathAnim
from anims.fall import FallAnim
from anims.flicker import FlickerAnim
from contexts.cutscene import CutsceneContext
from contexts.dialogue import DialogueContext
from transits.dissolve import DissolveIn, DissolveOut
from lib.cell import add as add_cell
import config
from config import RUN_DURATION, TILE_SIZE

class AltarRoom(SpecialRoom):
  def __init__(room, *args, **kwargs):
    super().__init__(degree=2, shape=[
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
      "         .         ",
      "         .         ",
      "         .         ",
      "         .         ",
      "         .         ",
    ], elems=[
      (altar_cell := (9, 5), altar := Altar(on_effect=room.on_trigger)),
      (add_cell(altar_cell, (0, 1)), mage := Mage(faction="ally", facing=(0, -1))),
      (add_cell(altar_cell, (-2, -3)), Pillar()),
      (add_cell(altar_cell, (-3, -2)), Pillar()),
      (add_cell(altar_cell, (-3, 0)), Pillar()),
      (add_cell(altar_cell, (-3, 2)), Pillar()),
      (add_cell(altar_cell, (-2, 3)), Pillar()),
      (add_cell(altar_cell, (2, 3)), Pillar()),
      (add_cell(altar_cell, (2, -3)), Pillar()),
      (add_cell(altar_cell, (3, -2)), Pillar()),
      (add_cell(altar_cell, (3, 0)), Pillar()),
      (add_cell(altar_cell, (3, 2)), Pillar()),
    ], *args, **kwargs)
    room.altar = altar
    room.mage = mage
    room.entered = False

  def get_edges(room):
    room_width, room_height = room.get_size()
    room_x, room_y = room.cell or (0, 0)
    return [
      (room_x + room_width // 2, room_y + room_height)
    ]

  def on_enter(room, game):
    super().on_enter(game)
    if not config.CUTSCENES or "minxia" in game.parent.story:
      game.floor.remove_elem(room.mage)
      room.mage = None
      return False
    game.open(CutsceneContext(script=[
      *(cutscene(room, game) if config.CUTSCENES else []),
      next_floor(game)
    ]))

  def on_trigger(room, game):
    game.open(CutsceneContext(script=[
      lambda step: game.camera.focus(
        cell=room.altar.cell,
        tween=True,
        speed=30,
        on_end=step
      ),
      *collapse(room, game),
      next_floor(game)
    ]))

  def create_floor(room, *args, **kwargs):
    floor = next(super().create_floor(use_edge=False, *args, **kwargs))
    floor.entrance = room.get_edges()[0]
    floor.set_tile_at(floor.entrance, floor.STAIRS_UP)
    yield floor

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
      game.hero.move_to(add_cell(room.altar.cell, (0, 2))),
      game.anims.append([PathAnim(
        target=game.hero,
        path=[add_cell(room.altar.cell, c) for c in [(0, 8), (0, 7), (0, 6), (0, 5), (0, 4), (0, 3), (0, 2)]],
        on_end=step
      )])
    ),
    lambda step: game.anims.append([PauseAnim(duration=30, on_end=step)]),
    lambda step: (
      game.camera.focus(
        cell=add_cell(room.altar.cell, (0, 2)),
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
                cell=room.altar.cell,
                speed=30,
                tween=True
              ),
              room.mage.move_to(add_cell(room.altar.cell, (-1, -1))),
              game.anims.append([PathAnim(
                target=room.mage,
                path=[add_cell(room.altar.cell, c) for c in [(0, 1), (-1, 1), (-1, 0), (-1, -1)]],
                period=RUN_DURATION,
                on_end=step
              )])
            ),
            lambda step: (
              room.mage.set_facing((0, 1)),
              game.hero.move_to(add_cell(room.altar.cell, (0, 1))),
              game.anims.append([PathAnim(
                target=game.hero,
                path=[add_cell(room.altar.cell, c) for c in [(0, 2), (0, 1)]],
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
    *collapse(room, game)
  ]

def next_floor(game):
  return lambda step: (
    game.get_head().transition(
      transits=(DissolveIn(), DissolveOut()),
      loader=Floor1.generate(game.parent.story),
      on_end=lambda floor: (
        game.use_floor(floor, generator=Floor1),
        step()
      )
    )
  )

def collapse(room, game):
  floor = game.floor
  return [
    *[(lambda cell: lambda step: (
      floor.set_tile_at(add_cell(room.altar.cell, cell), floor.PIT),
      game.redraw_tiles(force=True),
      game.anims.append([PauseAnim(duration=5, on_end=step)]),
    ))(c) for c in [(-1, -2), (0, -2), (1, -2), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]],
    lambda step: game.anims.append([PauseAnim(duration=30, on_end=step)]),
    lambda step: (
      game.anims.extend([
        [
          ShakeAnim(
            target=game.hero,
            duration=30,
            on_end=lambda: game.anims[0].append(
              FallAnim(
                target=game.hero,
                y=game.hero.cell[1] * TILE_SIZE,
                dest=(
                  (next( # TODO: refactor into `find_nearest_non_pit_cell(cell)` or `find_pit_depth(cell)`
                    (y for y in range(game.hero.cell[1], floor.get_height())
                      if floor.get_tile_at((game.hero.cell[0], y)) is not floor.PIT),
                    floor.get_height()
                  ) - game.hero.cell[1]) * TILE_SIZE
                ),
                on_end=lambda: floor.remove_elem(game.hero)
              )
            )
          ),
          ShakeAnim(
            target=room.mage,
            duration=30,
            on_end=lambda: game.anims[0].append(
              FallAnim(
                target=room.mage,
                y=room.mage.cell[1] * TILE_SIZE,
                dest=(
                  (next(
                    (y for y in range(room.mage.cell[1], floor.get_height())
                      if floor.get_tile_at((room.mage.cell[0], y)) is not floor.PIT),
                    floor.get_height()
                  ) - room.mage.cell[1]) * TILE_SIZE
                ),
                on_end=lambda: floor.remove_elem(room.mage)
              )
            )
          ),
          PauseAnim(duration=60)
        ],
        [PauseAnim(
          duration=30,
          on_end=step
        )]
      ])
    )
  ]
