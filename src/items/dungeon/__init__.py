from dataclasses import dataclass
from items import Item
from assets import load as use_assets
from palette import GREEN

@dataclass
class DungeonItem(Item):
  color: int = GREEN
  effect: str = None
  PAUSE_DURATION: int = 60

  def use(item, game):
    return True, "But nothing happened..."
