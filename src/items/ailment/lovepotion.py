from dataclasses import dataclass
from items.ailment import AilmentItem

@dataclass
class LovePotion(AilmentItem):
  name: str = "LovePotion"
  desc: str = "Inflicts charm."
  ailment: str = "charm"
  value: int = 48

  def use(item, store):
    return False, "You can't use that here!"

  def effect(item, game, actor):
    actor.inflict_ailment("sleep")
    game.log.print((actor.token(), " fell asleep!"))
