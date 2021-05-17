from town.actors.npc import Npc
from cores.mage import MageCore
from assets import load as use_assets
from filters import replace_color
from palette import BLACK, GREEN

class MageNpc(Npc):
  def __init__(mage, messages=None):
    super().__init__(MageCore(), messages)
    mage.core.faction = "ally"
    mage.draws = 0

  def render(mage):
    sprites = use_assets().sprites
    image = sprites["mage"]
    image = replace_color(image, BLACK, GREEN)
    mage.sprite.image = image
    return super().render()
