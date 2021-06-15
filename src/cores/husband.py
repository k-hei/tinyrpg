from cores.biped import BipedCore, SpriteMap

class HusbandCore(BipedCore):
  sprites = SpriteMap(
    face_right="husband",
    face_down="husband",
    face_up="husband",
    walk_right=("husband_walk", "husband", "husband_walk", "husband"),
    walk_down=("husband_walk", "husband", "husband_walk", "husband"),
    walk_up=("husband_walk", "husband", "husband_walk", "husband")
  )

  def __init__(husband, name="Thag"):
    super().__init__(
      name=name,
      faction="ally"
    )
