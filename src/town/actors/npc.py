from town.actors import Actor

class Npc(Actor):
  def __init__(npc, name, message=None):
    super().__init__(name)
    npc.message = message
