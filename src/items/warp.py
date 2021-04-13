from assets import load as use_assets

class WarpCrystal:
  def __init__(warp):
    warp.name = "Warp Crystal"
    warp.description = "Return to town"

  def effect(warp, game):
    return (True, "But nothing happened...")

  def render(warp):
    assets = use_assets()
    return assets.sprites["icon_crystal"]
