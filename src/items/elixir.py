from assets import load as use_assets

class Elixir:
  def __init__(elixir):
    elixir.name = "Elixir"
    elixir.desc = "Restores full HP and SP"

  def effect(potion, game):
    hero = game.hero
    ally = game.ally
    if hero.hp < hero.hp_max or ally.hp < ally.hp_max or game.sp < game.sp_max:
      hero.hp = hero.hp_max
      ally.hp = ally.hp_max
      game.sp = game.sp_max
      return (True, "The party restored full HP and SP.")
    else:
      return (False, "Nothing to restore!")

  def render(elixir):
    return use_assets().sprites["icon_elixir"]
