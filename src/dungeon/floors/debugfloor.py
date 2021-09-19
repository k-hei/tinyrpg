import assets
from dungeon.floors import Floor
from dungeon.gen import gen_floor

class DebugFloor(Floor):
  def generate(store=None, seed=None):
    return gen_floor(
      rooms=[assets.rooms["exitroom"], assets.rooms["oasisroom"]],
      seed=seed
    )
