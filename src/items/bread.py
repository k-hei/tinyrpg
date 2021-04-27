from assets import load as use_assets

class Bread:
  def __init__(bread):
    bread.sp = 10
    bread.name = "Bread"
    bread.kind = "sp"
    bread.desc = "Restores " + str(bread.sp) + " SP."

  def effect(bread, ctx):
    game = ctx.parent
    if game.sp < game.sp_max:
      game.sp = min(game.sp_max, game.sp + bread.sp)
      return (True, "The party restored " + str(bread.sp) + " SP.")
    else:
      return (False, "Your stamina is already full!")

  def render(bread):
    return use_assets().sprites["icon_bread"]
