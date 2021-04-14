from actors import Actor

class Mimic(Actor):
  def __init__(mimic):
    super().__init__(
      name="Mimic",
      faction="enemy",
      hp=5,
      st=5,
      en=1
    )
    mimic.idle = True

  def activate(mimic):
    mimic.idle = False
