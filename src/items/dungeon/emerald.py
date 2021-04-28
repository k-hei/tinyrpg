from dataclasses import dataclass
from items.dungeon import DungeonItem
from anims.pause import PauseAnim

@dataclass(frozen=True)
class Emerald(DungeonItem):
  name: str = "Emerald"
  desc: str = "Returns to town."
  effect: str = "leave_dungeon"

  def use(emerald, game):
    game.anims.append([
      PauseAnim(duration=DungeonItem.PAUSE_DURATION, on_end=game.leave_dungeon)
    ])
    return True, "You take the balloon to the next floor."
