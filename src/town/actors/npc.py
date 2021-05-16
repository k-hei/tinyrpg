from town.actors import Actor

class Npc(Actor):
  def __init__(npc, core, messages=None):
    super().__init__(core)
    core.faction = "ally"
    npc.messages = messages
    npc.message_index = 0
