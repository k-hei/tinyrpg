from config import MOVE_DURATION
from town.actors import Actor

class Knight(Actor):
  def __init__(knight, core):
    super().__init__(core)

  def render(knight):
    return knight.core.render()
