from assets import load as use_assets

class Potion:
  def __init__(potion):
    potion.hp = 5
    potion.name = "Potion"
    potion.description = "Restores " + str(potion.hp) + " HP"

  def effect(potion, game):
    hero = game.hero
    if hero.hp < hero.hp_max:
      hero.hp = min(hero.hp_max, hero.hp + potion.hp)
      return (True, "Restored " + str(potion.hp) + " HP.")
    else:
      return (False, "Your health is already full!")

  def render(potion):
    assets = use_assets()
    return assets.sprites["icon_potion"]
