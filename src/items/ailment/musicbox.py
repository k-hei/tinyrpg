from dataclasses import dataclass
from items.ailment import AilmentItem

@dataclass
class MusicBox(AilmentItem):
  name: str = "MusicBox"
  desc: str = "Inflicts sleep."
  ailment: str = "charm"
  value: int = 36

  def use(item, store):
    if type(store.place).__name__.startswith("Town"):
      return False, "You can't use that here!"
    return True, item.effect(store.place)

  def effect(item, game, actor=None):
    actor = actor or game.hero
    actor.inflict_ailment("sleep")
    return (actor.token(), " fell asleep!")
