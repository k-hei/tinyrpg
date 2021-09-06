from dataclasses import dataclass
from items.ailment import AilmentItem
from dungeon.actors import DungeonActor
from vfx.burst import BurstVfx
from colors.palette import VIOLET
from skills.ailment.virus import Virus

@dataclass
class Booze(AilmentItem):
  name: str = "Booze"
  desc: str = "Hazardous to your health."
  sprite: str = "vino"
  ailment: str = "poison"
  value: int = 32
  fragile: bool = True

  def use(item, store):
    if type(store.place).__name__.startswith("Town"):
      return False, "You can't use that here!"
    game = store.place
    return True, item.effect(game, actor=game.hero)

  def effect(item, game, actor=None, cell=None):
    if cell:
      game.vfx.append(BurstVfx(
        cell=cell,
        color=VIOLET
      ))
      Virus.spawn_cloud(game, cell, inclusive=True)
    if actor:
      actor.inflict_ailment("poison")
      return (actor.token(), " is poisoned.")
