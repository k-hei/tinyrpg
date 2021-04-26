from assets import load as use_assets
from anims.pause import PauseAnim
import config

class Balloon:
  def __init__(balloon):
    balloon.name = "Balloon"
    balloon.desc = "Ascend to the next floor"

  def effect(balloon, game):
    if game.get_floor_no() < config.TOP_FLOOR:
      game.anims.append([
        PauseAnim(duration=240, on_end=game.ascend)
      ])
      return (True, "You take the balloon to the next floor.")
    else:
      return (False, "There's nowhere to go up here!")

  def render(balloon):
    return use_assets().sprites["icon_balloon"]
