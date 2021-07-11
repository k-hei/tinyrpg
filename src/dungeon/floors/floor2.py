from dungeon.gen import gen_floor, FloorGraph
from dungeon.features.vertroom import VerticalRoom
from dungeon.features.exitroom import ExitRoom
from dungeon.features.arenaroom import ArenaRoom

def Floor2():
  entry_room = VerticalRoom(size=(3, 4), degree=1)
  arena_room = ArenaRoom()
  exit_room = ExitRoom()
  return gen_floor(
    entrance=entry_room,
    features=FloorGraph(
      nodes=[entry_room, arena_room, exit_room],
      edges=[
        (entry_room, arena_room),
        (arena_room, exit_room),
      ]
    )
  )
