from town.actors import Actor

class Mage(Actor):
  def __init__(mage, core):
    super().__init__(core)

  def render(mage):
    return mage.core.render()
