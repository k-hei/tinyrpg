from random import randint
from dungeon.floors import Floor
from dungeon.gen import gen_floor, gen_enemy, FloorGraph
from dungeon.features.vertroom import VerticalRoom
from dungeon.features.exitroom import ExitRoom
from dungeon.features.arenaroom import ArenaRoom
from dungeon.features.pushblockroom import PushBlockRoom
from dungeon.features.puzzleroom import PuzzleRoom
from dungeon.features.oasisroom import OasisRoom
from dungeon.features.enemyroom import EnemyRoom
from dungeon.actors.eye import Eyeball
from dungeon.actors.mushroom import Mushroom
from dungeon.actors.skeleton import Skeleton
from dungeon.actors.genie import Genie

from lib.cell import add as add_cell
from anims.flicker import FlickerAnim
from contexts.dialogue import DialogueContext
from contexts.cutscene import CutsceneContext

class Floor2(Floor):
  scripts = [
    ("tiles", lambda game: CutsceneContext(script=[
      lambda step: game.child.open(DialogueContext(script=[
        (game.talkee.get_name(), "The tiles you stand on can have different combat effects."),
        (game.talkee.get_name(), "Use the environment to boost your chances of survival in the dungeon.")
      ]), on_close=step),
      lambda step: (
        game.anims.append([FlickerAnim(
          target=game.talkee,
          duration=45,
          on_end=lambda: (
            game.floor.remove_elem(game.talkee),
            step()
          )
        )])
      )
    ])),
    ("items", lambda game: CutsceneContext(script=[
      lambda step: game.child.open(DialogueContext(script=[
        (game.talkee.get_name(), "How are you doing on items?"),
        (game.talkee.get_name(), "You may want to make sure you're well stocked up before proceeding.")
      ]), on_close=step),
      lambda step: (
        game.anims.append([FlickerAnim(
          target=game.talkee,
          duration=45,
          on_end=lambda: (
            game.floor.remove_elem(game.talkee),
            step()
          )
        )])
      )
    ]))
  ]

  def generate():
    entry_room = VerticalRoom(size=(3, 4), degree=1)
    pushblock_room = PushBlockRoom(degree=2)
    buffer_room1 = VerticalRoom(
      size=(3, 4),
      degree=2,
      on_place=lambda room, stage: (
        stage.spawn_elem_at(add_cell((0, 0), room.cell), Genie(
          name="Joshin",
          message=next((s for s in Floor2.scripts if s[0] == "tiles"), None)
        ))
      )
    )
    buffer_room2 = EnemyRoom(size=(5, 7), degree=2, enemies=[
      gen_enemy(Skeleton),
      gen_enemy(Mushroom),
      gen_enemy(Eyeball),
    ])
    puzzle_room = PuzzleRoom(degree=2)
    buffer_room3 = VerticalRoom(
      size=(3, 4),
      degree=2,
      on_place=lambda room, stage: (
        stage.spawn_elem_at(add_cell((room.get_width() - 1, 0), room.cell), Genie(
          name="Joshin",
          message=next((s for s in Floor2.scripts if s[0] == "items"), None)
        ))
      )
    )
    arena_room = ArenaRoom()
    exit_room = ExitRoom()
    oasis_room = OasisRoom()
    enemy_room = EnemyRoom(size=(3, 4), degree=1, enemies=[
      gen_enemy(Skeleton, rare=True),
      gen_enemy(Eyeball),
      gen_enemy(Eyeball),
    ])

    return gen_floor(
      size=(23, 42),
      entrance=entry_room,
      features=FloorGraph(
        nodes=[buffer_room2, puzzle_room, buffer_room3, arena_room, exit_room, oasis_room, entry_room, pushblock_room, buffer_room1, enemy_room],
        edges=[
          (buffer_room2, puzzle_room),
          (puzzle_room, buffer_room3),
          (buffer_room3, arena_room),
          (arena_room, exit_room),
          (entry_room, pushblock_room),
          (pushblock_room, buffer_room1),
        ]
      )
    )
