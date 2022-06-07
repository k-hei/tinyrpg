from dataclasses import dataclass
from items.ailment import AilmentItem
from colors.palette import GOLD
from anims.pause import PauseAnim

@dataclass
class Topaz(AilmentItem):
  name: str = "Topaz"
  desc: str = "????"
  sprite: str = "gem"
  color: int = GOLD
  value: int = 200

  def use(topaz, store):
    if type(store.place).__name__.startswith("Town"):
      return False, "You can't use that here!"

    game = store.place
    hero = game.hero
    hero.inflict_ailment("invulnerable")
    game.anims.append([PauseAnim(duration=30)])
    return True, (hero.token(), " surges with power!")
