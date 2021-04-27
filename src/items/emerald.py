from assets import load as use_assets
from anims.pause import PauseAnim
import config

class Emerald:
  def __init__(emerald):
    emerald.name = "Emerald"
    emerald.kind = "dungeon"
    emerald.desc = "Returns to town."

  def effect(emerald, game):
    game.anims.append([
      PauseAnim(duration=240, on_end=game.leave_dungeon)
    ])
    return (True, "The gem's return magic has activated.")

  def render(emerald):
    return use_assets().sprites["icon_emerald"]
