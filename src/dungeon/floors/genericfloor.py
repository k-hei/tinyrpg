from dungeon.floors import Floor
from dungeon.gen import gen_floor, gen_enemy, FloorGraph

class GenericFloor(Floor):
  def generate(story):
    return gen_floor(size=(27, 27))
