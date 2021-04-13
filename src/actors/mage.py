from actors.actor import Actor
from skills.somnus import Somnus

class Mage(Actor):
  def __init__(mage):
    super().__init__(
      name="Mage",
      faction="player",
      hp=7,
      st=3,
      en=0,
      skill=Somnus()
    )
