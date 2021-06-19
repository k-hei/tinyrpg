from cores.biped import BipedCore, SpriteMap

class HusbandCore(BipedCore):
  name = "Thag"
  sprites = SpriteMap(
    face_right="husband",
    face_down="husband",
    face_up="husband",
    walk_right=("husband_walk", "husband", "husband_walk", "husband"),
    walk_down=("husband_walk", "husband", "husband_walk", "husband"),
    walk_up=("husband_walk", "husband", "husband_walk", "husband")
  )

  def __init__(husband, name=None):
    super().__init__(
      name=name or HusbandCore.name,
      faction="ally"
    )
