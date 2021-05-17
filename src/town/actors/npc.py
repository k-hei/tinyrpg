from config import TILE_SIZE
from town.actors import Actor

class Npc(Actor):
  def __init__(npc, core, messages=None):
    super().__init__(core)
    core.faction = "ally"
    npc.y -= TILE_SIZE // 2
    npc.messages = messages
    npc.message_index = 0
