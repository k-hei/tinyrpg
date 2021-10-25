from dataclasses import dataclass
from items.dungeon import DungeonItem
from anims.pause import PauseAnim
from lib.compose import compose

@dataclass
class Emerald(DungeonItem):
  name: str = "Emerald"
  desc: str = "Returns to town."
  sprite: str = "gem"
  effect: str = "leave_dungeon"
  value: int = 80
  rarity: int = 2

  def use(emerald, store):
    if type(store.place).__name__.startswith("Town"):
      return False, "You can't use this here!"

    game = store.place
    pause_anim = game.anims and next((a for a in game.anims[0] if type(a) is PauseAnim), None)
    if pause_anim:
      pause_anim.duration = DungeonItem.PAUSE_DURATION
      pause_anim.on_end = compose(pause_anim.on_end, game.leave_dungeon)
    else:
      game.anims.append([
        PauseAnim(duration=DungeonItem.PAUSE_DURATION, on_end=game.leave_dungeon)
      ])
    return True, "The gem's return magic has activated."
