from dungeon.floors import Floor
from dungeon.gen import gen_floor, gen_enemy, FloorGraph
from dungeon.features.vertroom import VerticalRoom
from dungeon.features.oasisroom import OasisRoom
from dungeon.features.coffinroom import CoffinRoom
from dungeon.features.traproom import TrapRoom

class DebugFloor(Floor):
  def generate(store):
    entry_room = VerticalRoom(size=(3, 4), degree=2)
    oasis_room = OasisRoom()
    coffin_room = CoffinRoom()
    trap_room = TrapRoom(degree=1)
    return gen_floor(
      size=(27, 27),
      entrance=entry_room,
      features=FloorGraph(
        nodes=[coffin_room, entry_room, oasis_room, trap_room],
        edges=[
          (coffin_room, trap_room),
          (coffin_room, entry_room),
          (coffin_room, oasis_room),
        ]
      )
    )
