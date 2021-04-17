from assets import load as use_assets

class Fish:
  def __init__(fish):
    fish.sp = 20
    fish.name = "Fish"
    fish.desc = "Restores " + str(fish.sp) + " SP"

  def effect(fish, game):
    if game.sp < game.sp_max:
      game.sp = min(game.sp_max, game.sp + fish.sp)
      return (True, "The party restored " + str(fish.sp) + " SP.")
    else:
      return (False, "Your stamina is already full!")

  def render(fish):
    return use_assets().sprites["icon_fish"]
