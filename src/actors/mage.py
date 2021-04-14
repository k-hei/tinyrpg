from actors import Actor
from skills.somnus import Somnus

class Mage(Actor):
  def __init__(mage):
    super().__init__(
      name="Mage",
      faction="player",
      hp=7,
      st=4,
      en=1,
      skill=Somnus()
    )
