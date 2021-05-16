from town.actors import Actor

class Npc(Actor):
  def __init__(npc, core, messages=None):
    super().__init__(core)
    npc.messages = messages
    npc.message_index = 1
