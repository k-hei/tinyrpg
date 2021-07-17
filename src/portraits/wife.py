from portraits import Portrait
from assets import assets

class WifePortrait(Portrait):
  def render(portrait):
    return super().render(assets.sprites["portrait_wife"])
