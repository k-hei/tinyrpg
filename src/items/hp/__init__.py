from dataclasses import dataclass
from items import Item
from colors.palette import RED

@dataclass
class HpItem(Item):
  color: int = RED
  hp: int = 0

  def use(item, store):
    hero = store.party[0]
    if hero.get_hp() < hero.get_hp_max():
      hero.heal(item.hp)
      return None, "Restored " + str(item.hp) + " HP."
    else:
      return False, "Your health is already full!"
