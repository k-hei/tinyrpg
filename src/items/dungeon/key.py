from dataclasses import dataclass
from items.dungeon import DungeonItem
from colors.palette import GOLD

@dataclass
class Key(DungeonItem):
  name: str = "Key"
  desc: str = "Opens a special door."
  color: tuple[int, int, int] = GOLD
  rarity: int = 2
  value: int = 1

  def use(key, game):
    return False, "There's nowhere to use this!"
