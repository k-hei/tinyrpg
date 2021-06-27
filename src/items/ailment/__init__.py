from dataclasses import dataclass
from items import Item
from assets import load as use_assets
from palette import VIOLET

@dataclass
class AilmentItem(Item):
  color: int = VIOLET
  ailment: str = ""

  def use(item, game):
    hero = game.hero
    if hero.ailment == item.ailment or item.ailment == "any" and hero.ailment != None:
      ailment = hero.ailment
      hero.dispel_ailment()
      return True, (hero.token(), "'s {} was cured.".format(ailment))
    elif item.ailment == "any":
      return False, "Nothing to dispel!"
    else:
      return False, ("No {} to dispel on ".format(item.ailment), hero.token(), ".")
