from random import randint
from dungeon.floors import Floor
from dungeon.gen import gen_floor, gen_enemy, FloorGraph
from dungeon.features.vertroom import VerticalRoom
from dungeon.features.hallroom import HallRoom
from dungeon.features.magebossroom import MageBossRoom
from dungeon.features.emeraldroom import EmeraldRoom

class Floor3(Floor):
  def generate():
    entry_room = VerticalRoom(size=(3, 4), degree=1)
    hall_room = HallRoom()
    mageboss_room = MageBossRoom()
    emerald_room = EmeraldRoom()
    return gen_floor(
      size=(21, 72),
      entrance=entry_room,
      features=FloorGraph(
        nodes=[entry_room, hall_room, mageboss_room, emerald_room],
        edges=[
          (entry_room, hall_room),
          (hall_room, mageboss_room),
          (mageboss_room, emerald_room),
        ]
      )
    )
