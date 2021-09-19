from lib.cell import add as add_vector
from dungeon.actors.mage import Mage

def on_focus(room, game):
  if "minxia" in game.store.story:
    return False
  room.mage = Mage(
    faction="ally",
    facing=(0, -1)
  )
  game.floor.spawn_elem_at(add_vector(room.center, (0, -1)), room.mage)
