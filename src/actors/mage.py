from actors.actor import Actor

class Mage(Actor):
  def __init__(mage):
    super().__init__(
      name="Mage",
      faction="player",
      hp=7,
      st=3,
      en=0
    )
