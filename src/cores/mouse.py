from cores import Stats
from cores.biped import BipedCore, SpriteMap

from assets import assets
from anims.frame import FrameAnim
from config import MOUSE_NAME


class Mouse(BipedCore):
  name = MOUSE_NAME
  sprites = SpriteMap(
    face_right="mouse",
    face_down="mouse_down",
    face_up="mouse_up",
    walk_right=("mouse_walk", "mouse", "mouse_walk", "mouse"),
    walk_down=("mouse_walkdown0", "mouse_down", "mouse_walkdown1", "mouse_down"),
    walk_up=("mouse_walkup0", "mouse_up", "mouse_walkup1", "mouse_up")
  )

  def __init__(mouse, faction="enemy", *args, **kwargs):
    super().__init__(
      name=Mouse.name,
      faction=faction,
      *args, **kwargs)
