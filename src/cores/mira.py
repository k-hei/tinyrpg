from cores.biped import BipedCore, SpriteMap

class MiraCore(BipedCore):
  name = "Mira"
  sprites = SpriteMap(
    face_right="mira",
    face_down="mira",
    face_up="mira",
    walk_right=("mira_walk", "mira", "mira_walk", "mira"),
    walk_down=("mira_walk", "mira", "mira_walk", "mira"),
    walk_up=("mira_walk", "mira", "mira_walk", "mira")
  )

  def __init__(mira, name=None):
    super().__init__(
      name=name or MiraCore.name,
      faction="ally"
    )
