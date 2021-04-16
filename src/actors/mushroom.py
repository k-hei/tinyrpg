from assets import load as use_assets
from actors import Actor

class Mushroom(Actor):
  def __init__(mushroom):
    super().__init__(
      name="Mushroom",
      faction="enemy",
      hp=38,
      st=17,
      en=9
    )

  def render(mushroom):
    assets = use_assets()
    return super().render(assets.sprites["mushroom"])
