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
from palette import BLACK, ORANGE

class Genie(Npc):
  def __init__(genie, name, script, color=ORANGE):
    super().__init__(GenieCore(name=name, color=color), script)

  def view(genie, anims=[]):
    return super().view(genie.core.view(), anims)
