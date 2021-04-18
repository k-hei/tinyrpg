from assets import load as use_assets
from actors import Actor

class Skeleton(Actor):
  def __init__(skeleton):
    super().__init__(
      name="Skeleton",
      faction="enemy",
      hp=30,
      st=16,
      en=9
    )

  def render(knight, anims):
    sprites = use_assets().sprites
    sprite = sprites["skeleton"]
    return super().render(sprite, anims)
