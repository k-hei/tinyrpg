from cores.biped import BipedCore, SpriteMap

class MiraCore(BipedCore):
  sprites = SpriteMap(
    face_right="mira",
    face_down="mira",
    face_up="mira",
    walk_right=("mira_walk", "mira", "mira_walk", "mira"),
    walk_down=("mira_walk", "mira", "mira_walk", "mira"),
    walk_up=("mira_walk", "mira", "mira_walk", "mira")
  )

  def __init__(mira, name="Mira"):
    super().__init__(
      name=name,
      faction="ally"
    )
