from actors import Actor

class Mage(Actor):
  def __init__(mage, skills):
    super().__init__(
      name="Mage",
      faction="player",
      hp=27,
      st=28,
      en=10,
      skills=skills
    )
