from assets import load as use_assets

class Potion:
  def __init__(potion):
    potion.hp = 20
    potion.name = "Potion"
    potion.desc = "Restores " + str(potion.hp) + " HP"

  def effect(potion, game):
    hero = game.hero
    if hero.get_hp() < hero.get_hp_max():
      hero.regen(potion.hp)
      return (True, "Restored " + str(potion.hp) + " HP.")
    else:
      return (False, "Your health is already full!")

  def render(potion):
    return use_assets().sprites["icon_potion"]
