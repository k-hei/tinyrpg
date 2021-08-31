from dataclasses import dataclass
from items.dungeon import DungeonItem
from anims.pause import PauseAnim

@dataclass
class Emerald(DungeonItem):
  name: str = "Emerald"
  desc: str = "Returns to town."
  sprite: str = "gem"
  effect: str = "leave_dungeon"
  value: int = 80

  def use(emerald, store):
    if type(store.place).__name__.startswith("Town"):
      return False, "You can't use this here!"

    game = store.place
    game.anims.append([
      PauseAnim(duration=DungeonItem.PAUSE_DURATION, on_end=game.leave_dungeon)
    ])
    return True, "The gem's return magic has activated."
