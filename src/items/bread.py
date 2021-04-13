from assets import load as use_assets

class Bread:
  def __init__(bread):
    bread.sp = 20
    bread.name = "Bread"
    bread.description = "Restores " + str(bread.sp) + " SP"

  def effect(bread, game):
    if game.sp < game.sp_max:
      game.sp = min(game.sp_max, game.sp + bread.sp)
      return (True, "The party restored " + str(bread.sp) + " SP.")
    else:
      return (False, "Your stamina is already full!")

  def render(bread):
    assets = use_assets()
    return assets.sprites["icon_bread"]
