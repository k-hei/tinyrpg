from town.actors.npc import Npc
from cores import Core
from assets import load as use_assets
from sprite import Sprite

class Rat(Npc):
  def __init__(rat, name, messages):
    super().__init__(Core(name=name, faction="ally"), messages)

  def render(rat):
    flip_x = rat.core.facing == (-1, 0)
    return Sprite(
      image=use_assets().sprites["rat"],
      flip=(flip_x, False)
    )
