from dataclasses import dataclass
from items.hp import HpItem
import lib.cell as cell

@dataclass(frozen=True)
class Ankh(HpItem):
  name: str = "Ankh"
  desc: str = "Revives ally with 50% HP."

  def use(ankh, game):
    hero = game.hero
    ally = game.ally
    floor = game.floor
    if not ally.dead:
      return False, "Your partner is still alive!"

    neighbors = cell.neighbors(hero.cell)
    neighbor = next((n for n in neighbors if floor.is_cell_empty(n)), None)
    if neighbor is None:
      return False, ("There's nowhere for ", ally.token(), " to spawn!")

    ally.set_hp(ally.get_hp_max() // 2)
    ally.dead = False
    floor.spawn_elem(ally, neighbor)
    return True, (ally.token(), " was revived.")
