from cores.biped import BipedCore, SpriteMap
from config import MAGE_NAME

class MageCore(BipedCore):
  sprites = SpriteMap(
    face_right="mage",
    face_down="mage_down",
    face_up="mage_up",
    walk_right=("mage_walk", "mage", "mage_walk", "mage"),
    walk_down=("mage_walkdown0", "mage_down", "mage_walkdown1", "mage_down"),
    walk_up=("mage_walkup0", "mage_up", "mage_walkup1", "mage_up")
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
