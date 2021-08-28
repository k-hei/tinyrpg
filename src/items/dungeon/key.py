from dataclasses import dataclass
from items.dungeon import DungeonItem
from colors.palette import GOLD

@dataclass
class Key(DungeonItem):
  name: str = "Key"
  desc: str = "Opens a special door."
  color: tuple[int, int, int] = GOLD

  def use(key, game):
    return False, "There's nowhere to use this!"
