from assets import load as use_assets
from text import render as render_text
from filters import recolor

PADDING_X = 10
PADDING_Y = 6
ICON_MARGIN = 6

class Skill():
  def __init__(skill, data):
    skill.data = data

  def render(option):
    skill = option.data
    assets = use_assets()
    font = assets.fonts["standard"]

    icon = get_icon(skill.kind)
    text = recolor(render_text(skill.name, font), (0xFF, 0xFF, 0xFF))
    surface = assets.sprites["skill"].copy()
    surface.blit(icon, (PADDING_X, PADDING_Y))
    surface.blit(text, (
      PADDING_X + icon.get_width() + ICON_MARGIN,
      PADDING_Y
    ))

    return surface

def get_icon(kind):
  assets = use_assets()
  if kind == "spell":
    return assets.sprites["icon_hat"]
  elif kind == "shield":
    return assets.sprites["icon_shield"]
  return None
