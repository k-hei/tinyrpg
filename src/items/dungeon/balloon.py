from dataclasses import dataclass
from items.dungeon import DungeonItem
from anims.pause import PauseAnim
import config

@dataclass
class Balloon(DungeonItem):
  name: str = "Balloon"
  desc: str = "Ascends to next floor."
  effect: str = "ascend"

  def use(balloon, game):
    if game.get_floor_no() < config.TOP_FLOOR:
      game.anims.append([
        PauseAnim(duration=DungeonItem.PAUSE_DURATION, on_end=game.ascend)
      ])
      return True, "You take the balloon to the next floor."
    else:
      return False, "There's nowhere to go up here!"
