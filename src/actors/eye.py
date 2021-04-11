from actors.actor import Actor

class Eye(Actor):
  def __init__(eye):
    super().__init__(
      name="Eyeball",
      faction="enemy",
      hp=5,
      st=3,
      en=1
    )
