from assets import load as use_assets
from actors import Actor

class Mushroom(Actor):
  def __init__(mushroom):
    super().__init__(
      name="Toadstool",
      faction="enemy",
      hp=55,
      st=17,
      en=9
    )

  def render(knight, anims):
    sprites = use_assets().sprites
    sprite = sprites["mushroom"]
    return super().render(sprite, anims)
