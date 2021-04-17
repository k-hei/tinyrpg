from assets import load as use_assets

class Emerald:
  def __init__(emerald):
    emerald.name = "Emerald"
    emerald.desc = "Return to town"

  def effect(emerald, game):
    return (True, "But nothing happened...")

  def render(emerald):
    return use_assets().sprites["icon_emerald"]
