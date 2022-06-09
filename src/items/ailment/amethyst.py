from dataclasses import dataclass
from items.ailment import AilmentItem

@dataclass
class Amethyst(AilmentItem):
  name: str = "Amethyst"
  desc: str = "Dispels all ailments."
  sprite: str = "gem"
  ailment: str = "any"
  value: int = 80

  def use(amethyst, store):
    if type(store.place).__name__.startswith("Town"):
      return False, "You can't use that here!"

    game = store.place
    hero = game.hero
    ally = game.ally

    if ((not hero or not hero.ailment)
    and (not ally or not ally.ailment)):
      return False, "Nothing to restore!"

    if hero and hero.ailment and ally and ally.ailment:
      hero.dispel_ailment()
      ally.dispel_ailment()
      return True, "The party's ailments were cured."

    if hero and hero.ailment:
      ailment = hero.ailment
      hero.dispel_ailment()
      return True, (hero.token(), f"'s {ailment} was cured.")

    if ally and ally.ailment:
      ailment = ally.ailment
      ally.dispel_ailment()
      return True, (ally.token(), f"'s {ailment} was cured.")
