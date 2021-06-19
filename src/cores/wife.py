from cores.biped import BipedCore, SpriteMap

class WifeCore(BipedCore):
  name = "Sylvia"
  sprites = SpriteMap(
    face_right="wife",
    face_down="wife",
    face_up="wife",
    walk_right=("wife_walk", "wife", "wife_walk", "wife"),
    walk_down=("wife_walk", "wife", "wife_walk", "wife"),
    walk_up=("wife_walk", "wife", "wife_walk", "wife")
  )

  def __init__(wife, name=None):
    super().__init__(
      name=name or WifeCore.name,
      faction="ally"
    )
