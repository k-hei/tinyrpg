from actors.actor import Actor

class Knight(Actor):
  def __init__(knight):
    super().__init__(
      name="Knight",
      faction="player",
      hp=9,
      st=4,
      en=1
    )
