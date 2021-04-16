from actors import Actor

class Eye(Actor):
  def __init__(eye):
    super().__init__(
      name="Eyeball",
      faction="enemy",
      hp=44,
      st=21,
      en=14
    )
