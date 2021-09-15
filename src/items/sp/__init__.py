from dataclasses import dataclass
from items import Item
from colors.palette import BLUE

@dataclass
class SpItem(Item):
  color: int = BLUE
  sp: int = 0

  def use(item, store):
    if store.sp < store.sp_max:
      store.sp += item.sp
      return None, "Restored " + str(item.sp) + " SP."
    else:
      return False, "Your stamina is already full!"
