from dataclasses import dataclass
from items.sp import SpItem

@dataclass
class Berry(SpItem):
  name: str = "Berry"
  desc: str = "Increases max SP."
  sp: int = 10
  value: int = 10

  def use(item, store):
    store.sp_max += item.sp
    store.sp += item.sp
    return True, "Max SP increased by {sp}.".format(sp=item.sp)
