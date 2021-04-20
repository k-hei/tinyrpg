from assets import load as use_assets
from actors import Actor
from skills.virus import Virus

class Mushroom(Actor):
  def __init__(mushroom):
    super().__init__(
      name="Toadstool",
      faction="enemy",
      hp=27,
      st=14,
      en=8,
      skills=[Virus]
    )

  def step(mushroom, game):
    super().step(game)

  def render(mushroom, anims):
    sprites = use_assets().sprites
    sprite = sprites["mushroom"]
    return super().render(sprite, anims)
