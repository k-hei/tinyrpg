from dataclasses import dataclass
from items.ailment import AilmentItem
from vfx.burst import BurstVfx
from colors.palette import GREEN
from contexts.cutscene import CutsceneContext

@dataclass
class LovePotion(AilmentItem):
  name: str = "LovePotion"
  desc: str = "Inflicts charm."
  ailment: str = "charm"
  value: int = 48
  rarity: int = 2

  def use(item, store):
    return False, "You can't use that here!"

  def effect(item, game, actor=None, cell=None):
    game.vfx.append(BurstVfx(
      cell=actor.cell,
      color=GREEN
    ))
    actor = actor or game.hero
    if actor.faction != "enemy":
      return False
    game.room and game.room.on_defeat(game, actor)
    # not isinstance(game.get_tail(), CutsceneContext) and game.exit(ally_rejoin=True)
    actor.faction = "ally"
    actor.aggro = False
    actor.behavior = "chase"
    actor.dispel_ailment()
