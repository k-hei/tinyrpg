from portraits import Portrait
from assets import load as use_assets
from anims.frame import FrameAnim

class WifePortrait(Portrait):
  def render(portrait):
    return super().render(use_assets().sprites["portrait_wife"])
