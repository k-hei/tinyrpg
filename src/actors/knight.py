from actors import Actor
from skills.blitzritter import Blitzritter

class Knight(Actor):
  def __init__(knight, skills):
    super().__init__(
      name="Knight",
      faction="player",
      hp=34,
      st=32,
      en=12,
      skills=skills
    )
