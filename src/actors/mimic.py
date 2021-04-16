from actors import Actor

class Mimic(Actor):
  def __init__(mimic):
    super().__init__(
      name="Mimic",
      faction="enemy",
      hp=38,
      st=17,
      en=9
    )
    mimic.idle = True

  def activate(mimic):
    mimic.idle = False
