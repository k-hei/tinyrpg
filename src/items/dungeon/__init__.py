from dataclasses import dataclass
from items import Item
from assets import load as use_assets
from colors.palette import GREEN

@dataclass
class DungeonItem(Item):
  color: int = GREEN
  effect: str = None
  PAUSE_DURATION: int = 120

  def use(item, game):
    return True, "But nothing happened..."
