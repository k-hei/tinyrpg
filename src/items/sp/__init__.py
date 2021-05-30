from dataclasses import dataclass
from items import Item
from palette import BLUE

@dataclass
class SpItem(Item):
  color: int = BLUE
  sp: int = 0

  def use(item, ctx):
    game = ctx.parent
    if game.sp < game.sp_max:
      game.sp = min(game.sp_max, game.sp + item.sp)
      return True, "Restored " + str(item.sp) + " SP."
    else:
      return False, "Your stamina is already full!"
