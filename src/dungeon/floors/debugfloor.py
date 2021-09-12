from random import randint
from dungeon.floors import Floor
from dungeon.gen.blob import gen_blob

class DebugFloor(Floor):
  def generate(store):
    return gen_floor()

def gen_floor():
  stage = gen_blob()
  stage.entrance = (stage.get_width() // 2, stage.get_height() // 2)
  yield stage
