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

  def use(topaz, game):
    hero = game.hero
    hero.inflict_ailment("invulnerable")
    game.anims.append([PauseAnim(duration=30)])
    return True, (hero.token(), "'s body is engulfed in a strange light.")
