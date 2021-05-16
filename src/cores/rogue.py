from cores.biped import BipedCore, SpriteMap
from config import ROGUE_NAME

class RogueCore(BipedCore):
  sprites = SpriteMap(
    face_right="rogue",
    walk_right="rogue_walk"
  )

  def __init__(rogue, name=ROGUE_NAME, skills=[]):
    super().__init__(
      name=name,
      faction="player",
      hp=17,
      st=14,
      en=7,
      skills=skills
    )
