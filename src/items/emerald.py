from assets import load as use_assets

class Emerald:
  def __init__(emerald):
    emerald.name = "Emerald"
    emerald.description = "Return to town"

  def effect(emerald, game):
    return (True, "But nothing happened...")

  def render(emerald):
    assets = use_assets()
    return assets.sprites["icon_emerald"]
