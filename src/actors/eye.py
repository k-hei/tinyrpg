from actors import Actor

class Eye(Actor):
  def __init__(eye):
    super().__init__(
      name="Eyeball",
      faction="enemy",
      hp=7,
      st=4,
      en=2
    )
