from dataclasses import dataclass
from items.ailment import AilmentItem
from vfx.burst import BurstVfx
from colors.palette import GREEN

@dataclass
class LovePotion(AilmentItem):
  name: str = "LovePotion"
  desc: str = "Inflicts charm."
  ailment: str = "charm"
  value: int = 48

  def use(item, store):
    return False, "You can't use that here!"

  def effect(item, game, actor=None):
    if actor.get_faction() != "enemy":
      return False
    actor = actor or game.hero
    actor.set_faction("ally")
    actor.aggro = False
    actor.behavior = "chase"
    game.vfx.append(BurstVfx(
      cell=actor.cell,
      color=GREEN
    ))
