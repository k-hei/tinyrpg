from actors import Actor
from skills.somnus import Somnus

class Mage(Actor):
  def __init__(mage):
    super().__init__(
      name="Mage",
      faction="player",
      hp=27,
      st=28,
      en=10,
      skill=Somnus()
    )
