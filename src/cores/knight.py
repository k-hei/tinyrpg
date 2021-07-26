from cores import Stats
from cores.biped import BipedCore, SpriteMap
from config import KNIGHT_NAME, KNIGHT_HP
import assets
from anims.frame import FrameAnim

class Knight(BipedCore):
  sprites = SpriteMap(
    face_right="knight",
    face_down="knight_down",
    face_up="knight_up",
    walk_right=("knight_walk", "knight", "knight_walk", "knight"),
    walk_down=("knight_walkdown0", "knight_down", "knight_walkdown1", "knight_down"),
    walk_up=("knight_walkup0", "knight_up", "knight_walkup1", "knight_up")
  )

  class SleepAnim(FrameAnim):
    frames = assets.sprites["knight_sleep"]
    frames_duration = 30

  class BlockAnim(FrameAnim):
    frames = assets.sprites["knight_block"]
    frames_duration = [6, 6, 33]

  class BlockUpAnim(FrameAnim):
    frames = assets.sprites["knight_blockup"]
    frames_duration = [6, 6, 33]

  class BlockDownAnim(FrameAnim):
    frames = assets.sprites["knight_blockdown"]
    frames_duration = [6, 6, 33]

  def __init__(knight, name=KNIGHT_NAME, faction="player", hp=KNIGHT_HP, *args, **kwargs):
    super().__init__(
      name=name,
      faction=faction,
      hp=hp,
      stats=Stats(
        hp=KNIGHT_HP,
        st=15,
        ma=3,
        dx=11,
        ag=7,
        lu=6,
        en=9
      ),
      *args,
      **kwargs
    )
