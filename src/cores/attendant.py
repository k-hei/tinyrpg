from cores.biped import BipedCore, SpriteMap
from contexts.dialogue import DialogueContext


class AttendantCore(BipedCore):
  name = "Attendant"
  sprites = SpriteMap(
    face_right="attendant",
    face_down="attendant",
    face_up="attendant",
    walk_right=("attendant_walk", "attendant", "attendant_walk", "attendant"),
    walk_down=("attendant_walk", "attendant", "attendant_walk", "attendant"),
    walk_up=("attendant_walk", "attendant", "attendant_walk", "attendant")
  )

  def __init__(attendant, name=None, *args, **kwargs):
    attendant_name = name or attendant.name
    super().__init__(
      name=attendant_name,
      faction="ally",
      message=lambda ctx: DialogueContext(script=[
        (attendant_name, "You must be the last arrival.")
      ]),
      *args, **kwargs,
    )
