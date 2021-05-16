from cores.biped import BipedCore, SpriteMap
from config import MAGE_NAME

class MageCore(BipedCore):
  sprites = SpriteMap(
    face_right="mage",
    walk_right="mage_walk",
    face_down="mage_down",
    walk_down="mage_walkdown"
  )

  def __init__(mage, name=MAGE_NAME, skills=[]):
    super().__init__(
      name=name,
      faction="player",
      hp=17,
      st=14,
      en=7,
      skills=skills
    )
