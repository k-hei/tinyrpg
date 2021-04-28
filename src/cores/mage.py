from cores import Core

class Mage(Core):
  def __init__(mage, skills=[]):
    super().__init__(
      name="Mage",
      faction="player",
      hp=17,
      st=14,
      en=7,
      skills=skills
    )
