from actors import Actor
from skills.blitzritter import Blitzritter

class Knight(Actor):
  def __init__(knight):
    super().__init__(
      name="Knight",
      faction="player",
      hp=9,
      st=12,
      en=2,
      skill=Blitzritter()
    )
