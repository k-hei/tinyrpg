from dungeon.actors.npc import Npc
from cores.genie import Genie as GenieCore
from assets import load as use_assets
from skills.weapon.tackle import Tackle
from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.awaken import AwakenAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from filters import replace_color
from palette import BLACK, GREEN

class Genie(Npc):
  def __init__(genie, name, script, color=GREEN):
    super().__init__(GenieCore(name), script)
    genie.color = color

  def render(genie, anims):
    sprite = genie.core.render()
    sprite.image = replace_color(sprite.image, BLACK, genie.color)
    return sprite
