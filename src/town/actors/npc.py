from town.actors import Actor

class Npc(Actor):
  def __init__(npc, core, message=None):
    super().__init__(core)
    npc.message = message
