from dataclasses import dataclass
from items.hp import HpItem

@dataclass
class Ruby(HpItem):
  name: str = "Ruby"
  desc: str = "Restores full HP."
  sprite: str = "gem"

  def use(ruby, ctx):
    game = ctx.parent
    hero = game.hero
    ally = game.ally
    if (hero.get_hp() < hero.get_hp_max()
    or ally.get_hp() < ally.get_hp_max()):
      hero.set_hp(hero.get_hp_max())
      ally.set_hp(ally.get_hp_max())
      return True, "The party restored full HP."
    else:
      return False, "Nothing to restore!"
