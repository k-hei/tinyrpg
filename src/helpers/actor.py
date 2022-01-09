from dungeon.actors.knight import Knight
from dungeon.actors.mage import Mage

def manifest_actor(core):
  core_id = type(core).__name__
  core_actors = {
    "Knight": Knight,
    "Mage": Mage,
  }
  return core_actors[core_id](core) if core_id in core_actors else None
