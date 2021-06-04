from dataclasses import dataclass
from items.hp import HpItem

@dataclass
class Elixir(HpItem):
  name: str = "Elixir"
  desc: str = "Restores full HP and SP."
  value: int = 100

  def use(elixir, ctx):
    game = ctx.parent
    hero = game.hero
    ally = game.ally
    if (hero.get_hp() < hero.get_hp_max()
    or ally.get_hp() < ally.get_hp_max()
    or game.sp < game.sp_max):
      hero.set_hp(hero.get_hp_max())
      ally.set_hp(ally.get_hp_max())
      game.sp = game.sp_max
      return True, "The party restored full HP and SP."
    else:
      return False, "Nothing to restore!"
