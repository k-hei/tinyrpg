from random import randint
from dungeon.gen import gen_floor, gen_enemy, FloorGraph
from dungeon.features.vertroom import VerticalRoom
from dungeon.features.hallroom import HallRoom
from dungeon.features.magebossroom import MageBossRoom

def Floor3():
  entry_room = VerticalRoom(size=(3, 4), degree=1)
  hall_room = HallRoom()
  mageboss_room = MageBossRoom()
  exit_room = VerticalRoom(size=(3, 4), degree=1)
  return gen_floor(
    size=(21, 42),
    entrance=entry_room,
    features=FloorGraph(
      nodes=[entry_room, mageboss_room, exit_room],
      edges=[
        (entry_room, mageboss_room),
        (mageboss_room, exit_room),
      ]
      # nodes=[entry_room, hall_room, mageboss_room, exit_room],
      # edges=[
      #   (entry_room, hall_room),
      #   (hall_room, mageboss_room),
      #   (mageboss_room, exit_room),
      # ]
    )
  )
