from dataclasses import dataclass
from items import Item
from skills import Skill
from colors.palette import GRAY

@dataclass
class EquipmentItem(Item):
  color: int = GRAY
  skill: Skill = None

  def use(item, store):
    return False, "You can't use this item!"
