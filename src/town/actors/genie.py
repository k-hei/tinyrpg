from town.actors.npc import Npc
from cores.genie import Genie as GenieCore

class Genie(Npc):
  def __init__(genie, name=None, messages=None):
    super().__init__(GenieCore(name), messages)

  def render(genie):
    genie.sprite = genie.core.render()
    return super().render()
