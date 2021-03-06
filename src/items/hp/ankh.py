from dataclasses import dataclass
from items.hp import HpItem
from lib.cell import neighborhood
from helpers.actor import manifest_actor
from helpers.stage import is_cell_walkable_to_actor

@dataclass
class Ankh(HpItem):
  name: str = "Ankh"
  desc: str = "Revives ally with 50% HP."
  value: int = 80
  rarity: int = 2

  def use(ankh, store):
    if type(store.place).__name__.startswith("Town"):
      return False, "You can't use that here!"

    game = store.place
    hero = game.hero
    floor = game.stage
    if not store.ally:
      return False, "No partner to revive!"

    if game.ally:
      return False, "Your partner is still alive!"

    ally = manifest_actor(store.ally)
    neighbors = neighborhood(hero.cell)
    neighbor = next((n for n in neighbors if is_cell_walkable_to_actor(floor, n, ally)), None)
    if neighbor is None:
      return False, ("There's nowhere for ", store.ally.token(), " to spawn!")

    ally.revive(1 / 2)
    floor.spawn_elem_at(neighbor, ally)
    return True, (ally.token(), " was revived.")
