from town.actors import Actor

class Npc(Actor):
  def __init__(npc, message=None):
    super().__init__()
    npc.message = message
