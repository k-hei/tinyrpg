from dataclasses import dataclass
from items.hp import HpItem
from vfx.burst import BurstVfx
from comps.damage import DamageValue
from colors.palette import GREEN

@dataclass
class Ruby(HpItem):
  name: str = "Ruby"
  desc: str = "Restores full HP."
  sprite: str = "gem"
  value: int = 100

  def use(ruby, store):
    if type(store.place).__name__.startswith("Town"):
      return False, "You can't use that here!"

    game = store.place
    hero = game.hero
    ally = game.ally
    if (hero.get_hp() < hero.get_hp_max()
    or ally and ally.get_hp() < ally.get_hp_max()):
      hero.set_hp(hero.get_hp_max())
      if ally:
        ally.set_hp(ally.get_hp_max())
      return True, "The party restored full HP."
    else:
      return False, "Nothing to restore!"

  def effect(potion, game, actor=None, cell=None):
    game.vfx.append(BurstVfx(
      pos=actor.pos,
      color=potion.color
    ))
    actor = actor or game.hero
    actor.regen(actor.get_hp_max())
    game.numbers.append(DamageValue(str(potion.hp), actor.cell, color=GREEN))
