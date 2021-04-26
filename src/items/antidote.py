from assets import load as use_assets

class Antidote:
  def __init__(antidote):
    antidote.name = "Antidote"
    antidote.desc = "Cures poison"

  def effect(antidote, game):
    hero = game.hero
    if hero.ailment == "poison":
      hero.ailment = None
      hero.ailment_turns = 0
      return (True, hero.name.upper() + "'s poison was cured.")
    else:
      return (False, hero.name.upper() + " isn't poisoned!")

  def render(antidote):
    return use_assets().sprites["icon_antidote"]
