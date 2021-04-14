from assets import load as use_assets
from text import render as render_text
from filters import recolor

class Skill():
  PADDING_X = 10
  PADDING_Y = 6
  ICON_MARGIN = 5

  def __init__(skill, data):
    skill.data = data

  def render(option):
    skill = option.data
    assets = use_assets()
    sprite = assets.sprites["skill"]
    font = assets.fonts["standard"]

    icon = get_icon(skill.kind)
    text = recolor(render_text(skill.name, font), (0xFF, 0xFF, 0xFF))

    surface = sprite.copy()
    surface.blit(icon, (Skill.PADDING_X, Skill.PADDING_Y))
    surface.blit(text, (
      Skill.PADDING_X + icon.get_width() + Skill.ICON_MARGIN,
      Skill.PADDING_Y
    ))

    return surface

def get_icon(kind):
  assets = use_assets()
  if kind == "spell":
    return assets.sprites["icon_hat"]
  elif kind == "shield":
    return assets.sprites["icon_shield"]
  return None
