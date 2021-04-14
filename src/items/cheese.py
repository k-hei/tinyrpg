from assets import load as use_assets

class Cheese:
  def __init__(cheese):
    cheese.sp = 5
    cheese.name = "Cheese"
    cheese.desc = "Restores " + str(cheese.sp) + " SP"

  def effect(cheese, game):
    if game.sp < game.sp_max:
      game.sp = min(game.sp_max, game.sp + cheese.sp)
      return (True, "The party restored " + str(cheese.sp) + " SP.")
    else:
      return (False, "Your stamina is already full!")

  def render():
    return use_assets().sprites["icon_cheese"]
