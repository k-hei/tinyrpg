from dataclasses import dataclass
from items.sp import SpItem

@dataclass
class Sapphire(SpItem):
  name: str = "Sapphire"
  desc: str = "Restores\nfull SP."
  sprite: str = "gem"
  value: int = 100

  def use(elixir, ctx):
    game = ctx.parent
    if game.sp < game.sp_max:
      game.sp = game.sp_max
      return True, "The party restored full SP."
    else:
      return False, "Nothing to restore!"
