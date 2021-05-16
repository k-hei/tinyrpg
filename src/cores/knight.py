from cores.biped import BipedCore, SpriteMap

class KnightCore(BipedCore):
  sprites = SpriteMap(
    face_right="knight",
    walk_right="knight_walk",
    face_down="knight_down",
    walk_down="knight_walkdown"
  )

  def __init__(knight, name="Knight", skills=[]):
    super().__init__(
      name=name,
      faction="player",
      hp=23,
      st=15,
      en=9,
      skills=skills
    )
