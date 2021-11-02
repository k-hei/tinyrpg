from dataclasses import dataclass
from items.ailment import AilmentItem

@dataclass
class MusicBox(AilmentItem):
  name: str = "MusicBox"
  desc: str = "Inflicts sleep."
  ailment: str = "sleep"
  value: int = 36
  rarity: int = 2

  def use(item, store):
    if type(store.place).__name__.startswith("Town"):
      return False, "You can't use that here!"
    return True, item.effect(store.place)

  def effect(item, game, actor=None, cell=None):
    actor = actor or game.hero
    actor.inflict_ailment("sleep")
    return (actor.token(), " fell asleep!")
