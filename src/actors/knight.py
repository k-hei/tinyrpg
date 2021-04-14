from actors import Actor
from skills.shieldbash import ShieldBash

class Knight(Actor):
  def __init__(knight):
    super().__init__(
      name="Knight",
      faction="player",
      hp=9,
      st=5,
      en=2,
      skill=ShieldBash()
    )
