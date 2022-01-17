from dataclasses import dataclass
from items.hp import HpItem
from vfx.burst import BurstVfx
from comps.damage import DamageValue
from colors.palette import GREEN

@dataclass
class Elixir(HpItem):
  name: str = "Elixir"
  desc: str = "Restores full HP and SP."
  value: int = 200
  rarity: int = 3

  def use(elixir, store):
    if type(store.place).__name__.startswith("Town"):
      return False, "You can't use that here!"

    ctx = store.place
    game = ctx.parent
    hero = ctx.hero
    ally = ctx.ally
    if (hero.get_hp() < hero.get_hp_max()
    or ally and ally.get_hp() < ally.get_hp_max()
    or game.store.sp < game.store.sp_max):
      hero.set_hp(hero.get_hp_max())
      ally and not ally.is_dead() and ally.set_hp(ally.get_hp_max())
      game.store.sp = game.store.sp_max
      return True, "The party restored full HP and SP."
    else:
      return False, "Nothing to restore!"

  def effect(potion, game, actor=None, cell=None):
    game.vfx.append(BurstVfx(
      pos=actor.pos,
      color=potion.color
    ))
    actor = actor or game.hero
    actor.regen(actor.get_max_hp())
    game.numbers.append(DamageValue(str(potion.hp), actor.cell, color=GREEN))
