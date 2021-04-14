from assets import load as use_assets
from text import render as render_text
from filters import recolor, outline
from pygame import Surface

PADDING_X = 10
PADDING_Y = 6
ICON_MARGIN = 6
TITLE_OVERLAP = 4

class Skill():
  def __init__(skill, data):
    skill.data = data

  def render(option):
    skill = option.data
    assets = use_assets()
    sprite = assets.sprites["skill"]
    font = assets.fonts["standard"]

    icon = get_icon(skill.kind)
    text = recolor(render_text(skill.name, font), (0xFF, 0xFF, 0xFF))
    title = render_text("SKILL", assets.fonts["smallcaps"])
    title = recolor(title, (0xFF, 0xFF, 0x00))
    title = outline(title, (0x00, 0x00, 0x00))

    surface = Surface((sprite.get_width(), sprite.get_height() + title.get_height() - TITLE_OVERLAP))
    surface.set_colorkey(0xFF00FF)
    surface.fill(0xFF00FF)

    offset = title.get_height() - TITLE_OVERLAP
    surface.blit(sprite, (0, offset))
    surface.blit(title, (PADDING_X, 0))
    surface.blit(icon, (PADDING_X, PADDING_Y + offset))
    surface.blit(text, (
      PADDING_X + icon.get_width() + ICON_MARGIN,
      PADDING_Y + offset
    ))

    return surface

def get_icon(kind):
  assets = use_assets()
  if kind == "spell":
    return assets.sprites["icon_hat"]
  elif kind == "shield":
    return assets.sprites["icon_shield"]
  return None
