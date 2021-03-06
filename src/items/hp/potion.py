from dataclasses import dataclass
from items.hp import HpItem
from vfx.burst import BurstVfx
from comps.damage import DamageValue
from colors.palette import GREEN

@dataclass
class Potion(HpItem):
  name: str = "Potion"
  desc: str = "Restores\n20 HP."
  hp: int = 20
  value: int = 25
  rarity: int = 2

  def effect(potion, game, actor=None, cell=None):
    game.vfx.append(BurstVfx(
      pos=actor.pos,
      color=potion.color
    ))
    actor = actor or game.hero
    actor.regen(potion.hp)
    game.vfx.append(DamageValue(str(potion.hp), actor.cell, color=GREEN))
