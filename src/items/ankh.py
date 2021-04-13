from assets import load as use_assets

class Ankh:
  def __init__(ankh):
    ankh.name = "Ankh"
    ankh.description = "Revives the dead with half HP"

  def effect(ankh, game):
    return (True, "But nothing happened...")

  def render(ankh):
    assets = use_assets()
    return assets.sprites["icon_ankh"]
