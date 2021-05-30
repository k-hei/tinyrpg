from dataclasses import dataclass
from items import Item
from palette import RED

@dataclass
class HpItem(Item):
  color: int = RED
  hp: int = 0

  def use(item, game):
    hero = game.hero
    if hero.get_hp() < hero.get_hp_max():
      hero.regen(item.hp)
      return True, "Restored " + str(item.hp) + " HP."
    else:
      return False, "Your health is already full!"
