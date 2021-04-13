from actors.actor import Actor

class Mimic(Actor):
  def __init__(mimic):
    super().__init__(
      name="Mimic",
      faction="enemy",
      hp=5,
      st=4,
      en=0
    )
    mimic.idle = True

  def activate(mimic):
    mimic.idle = False
