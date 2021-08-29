from dataclasses import dataclass
from items import Item
from colors.palette import BLUE

@dataclass
class SpItem(Item):
  color: int = BLUE
  sp: int = 0

  def use(item, ctx):
    game = ctx.parent
    if game.store.sp < game.store.sp_max:
      game.store.sp += item.sp
      return True, "Restored " + str(item.sp) + " SP."
    else:
      return False, "Your stamina is already full!"
