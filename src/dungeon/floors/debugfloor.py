from random import randint
from dungeon.floors import Floor
from dungeon.gen import gen_floor, gen_enemy, FloorGraph
from dungeon.features.vertroom import VerticalRoom
from dungeon.features.irregularroom import IrregularRoom

class DebugFloor(Floor):
  def generate(store):
    entry_room = VerticalRoom(size=(3, 4), degree=2)
    return gen_floor(
      size=(27, 27),
      entrance=entry_room,
      features=FloorGraph(
        nodes=[
          entry_room,
          *[IrregularRoom() for _ in range(randint(0, 2))]
        ]
      )
    )
