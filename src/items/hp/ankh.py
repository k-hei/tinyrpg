from dataclasses import dataclass
from items.hp import HpItem
import lib.cell as cell

@dataclass
class Ankh(HpItem):
  name: str = "Ankh"
  desc: str = "Revives ally with 50% HP."
  value: int = 80

  def use(ankh, store):
    if type(store.place).__name__.startswith("Town"):
      return False, "You can't use that here!"

    game = store.place
    hero = game.hero
    ally = game.ally
    floor = game.floor
    if not ally.is_dead():
      return False, "Your partner is still alive!"

    neighbors = cell.neighbors(hero.cell)
    neighbor = next((n for n in neighbors if floor.is_cell_empty(n)), None)
    if neighbor is None:
      return False, ("There's nowhere for ", ally.token(), " to spawn!")

    ally.revive(1 / 2)
    floor.spawn_elem_at(neighbor, ally)
    return True, (ally.token(), " was revived.")
