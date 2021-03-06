from cores import Stats
from cores.biped import BipedCore, SpriteMap
from config import ROGUE_NAME, ROGUE_HP

class Rogue(BipedCore):
  sprites = SpriteMap(
    face_right="rogue",
    face_down="rogue_down",
    face_up="rogue_up",
    walk_right=("rogue_walk", "rogue", "rogue_walk", "rogue"),
    walk_down=("rogue_walkdown0", "rogue_down", "rogue_walkdown1", "rogue_down"),
    walk_up=("rogue_walkup0", "rogue_up", "rogue_walkup1", "rogue_up")
  )

  def __init__(rogue, name=ROGUE_NAME, faction="player", hp=ROGUE_HP, *args, **kwargs):
    super().__init__(
      name=name,
      faction=faction,
      hp=hp,
      stats=Stats(
        hp=ROGUE_HP
      ),
      *args,
      **kwargs
    )
