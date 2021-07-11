from random import randint
from dungeon.gen import gen_floor, FloorGraph
from dungeon.features.vertroom import VerticalRoom
from dungeon.features.exitroom import ExitRoom
from dungeon.features.arenaroom import ArenaRoom
from dungeon.features.pushblockroom import PushBlockRoom
from dungeon.features.oasisroom import OasisRoom
from dungeon.features.enemyroom import EnemyRoom
from dungeon.actors.eye import Eye as Eyeball
from dungeon.actors.mushroom import Mushroom
from dungeon.actors.skeleton import Skeleton

def gen_enemy(Enemy, *args, **kwargs):
  return Enemy(
    ailment=("sleep" if randint(1, 3) == 1 else None),
    *args, **kwargs
  )

def Floor2():
  entry_room = VerticalRoom(size=(3, 4), degree=1)
  puzzle_room = PushBlockRoom(degree=2)
  buffer_room1 = EnemyRoom(size=(5, 7), degree=2, enemies=[
    gen_enemy(Skeleton),
    gen_enemy(Mushroom),
    gen_enemy(Eyeball),
  ])
  buffer_room2 = VerticalRoom(size=(3, 4), degree=2)
  arena_room = ArenaRoom()
  exit_room = ExitRoom()
  oasis_room = OasisRoom()
  enemy_room = EnemyRoom(size=(3, 4), degree=1, enemies=[
    gen_enemy(Skeleton, rare=True),
    gen_enemy(Eyeball),
    gen_enemy(Eyeball),
  ])

  return gen_floor(
    size=(21, 36),
    entrance=entry_room,
    features=FloorGraph(
      nodes=[entry_room, buffer_room1, puzzle_room, buffer_room2, arena_room, exit_room, oasis_room, enemy_room],
      edges=[
        (buffer_room1, puzzle_room),
        (puzzle_room, buffer_room2),
        (buffer_room2, arena_room),
        (arena_room, exit_room),
      ]
    )
  )
