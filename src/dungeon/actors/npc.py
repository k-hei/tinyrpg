from dungeon.actors import DungeonActor
from cores import Core
from assets import load as use_assets

class Npc(DungeonActor):
  def __init__(npc, core, script):
    super().__init__(core)
    npc.script = script

  def render(npc, sprite):
    return super().render(sprite)
