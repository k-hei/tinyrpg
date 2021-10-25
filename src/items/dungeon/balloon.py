from dataclasses import dataclass
from items.dungeon import DungeonItem
from anims.pause import PauseAnim
import config

@dataclass
class Balloon(DungeonItem):
  name: str = "Balloon"
  desc: str = "Ascends to next floor."
  effect: str = "ascend"
  value: int = 40
  rarity: int = 2

  def use(balloon, store):
    if type(store.place).__name__.startswith("Town"):
      return False, "You can't use this here!"
    game = store.place
    game.anims.append([
      PauseAnim(duration=DungeonItem.PAUSE_DURATION, on_end=game.ascend)
    ])
    return True, "You take the balloon to the next floor."
