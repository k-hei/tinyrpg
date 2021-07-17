from portraits import Portrait
from assets import assets

class HusbandPortrait(Portrait):
  def render(portrait):
    return super().render(assets.sprites["portrait_husband"])
