from town.actors import Actor

class Rogue(Actor):
  def __init__(rogue, core):
    super().__init__(core)

  def render(rogue):
    return rogue.core.render()
