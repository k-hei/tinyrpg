from town.actors.npc import Npc
from cores.mage import MageCore

class MageNpc(Npc):
  def __init__(mage, messages=None):
    super().__init__(MageCore(), messages)
    mage.core.faction = "ally"

  def render(mage):
    return mage.core.render()
