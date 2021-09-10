from dungeon.floors import Floor
from dungeon.gen import gen_floor, gen_enemy, FloorGraph
from dungeon.features.vertroom import VerticalRoom
from dungeon.features.irregularroom import IrregularRoom

class DebugFloor(Floor):
  def generate(store):
    entry_room = VerticalRoom(size=(3, 4), degree=2)
    irregular_room = IrregularRoom()
    return gen_floor(
      size=(17, 18),
      entrance=entry_room,
      features=FloorGraph(
        nodes=[irregular_room, entry_room],
        edges=[
          (entry_room, irregular_room)
        ]
      )
    )
