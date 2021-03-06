from dataclasses import dataclass
from items import Item
from assets import load as use_assets
from colors.palette import VIOLET
from vfx.burst import BurstVfx

@dataclass
class AilmentItem(Item):
  color: int = VIOLET
  ailment: str = ""

  def use(item, store):
    if type(store.place).__name__.startswith("Town"):
      return False, "You can't use that here!"

    game = store.place
    hero = game.hero
    if hero.ailment == item.ailment or item.ailment == "any" and hero.ailment != None:
      ailment = hero.ailment
      hero.dispel_ailment()
      return None, (hero.token(), "'s {} was cured.".format(ailment))
    elif item.ailment == "any":
      return False, "Nothing to dispel!"
    else:
      return False, ("No {} to dispel on ".format(item.ailment), hero.token(), ".")

  def effect(item, game, actor=None, cell=None):
    actor = actor or game.hero
    game.vfx.append(BurstVfx(
      cell=actor.cell,
      color=VIOLET
    ))
    if actor.ailment == item.ailment or item.ailment == "any" and actor.ailment != None:
      actor.dispel_ailment()
