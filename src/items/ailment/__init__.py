from dataclasses import dataclass
from items import Item
from assets import load as use_assets
from palette import PURPLE

@dataclass(frozen=True)
class AilmentItem(Item):
  color: tuple[int, int, int] = PURPLE
  ailment: str = ""

  def use(item, game):
    hero = game.hero
    if hero.ailment == item.ailment:
      hero.ailment = None
      hero.ailment_turns = 0
      return True, (hero.token(), "'s {} was cured.".format(item.ailment))
    else:
      return False, ("No {} to dispel on ".format(item.ailment), hero.token(), ".")
