import assets
from dungeon.floors import Floor
from dungeon.gen import gen_floor

class DebugFloor(Floor):
  def generate(store=None, seed=None):
    return gen_floor(
      rooms=[
        assets.rooms["exit_room"],
        assets.rooms["oasis_room"],
        assets.rooms["mageboss_room"],
      ],
      seed=seed
    )
