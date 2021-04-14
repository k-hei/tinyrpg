from assets import load as use_assets()

class Skill():
  def __init__(skill, data):
    skill.data = data

  def render(skill):
    assets = use_assets()
    surface = assets.sprites["skill"].copy()
    return surface
