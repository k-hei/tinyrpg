from cores import Core

class Knight(Core):
  def __init__(knight, skills=[]):
    super().__init__(
      name="Knight",
      faction="player",
      hp=23,
      st=15,
      en=9,
      skills=skills
    )
