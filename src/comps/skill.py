from assets import load as use_assets
from text import render as render_text
from filters import recolor, outline, replace_color
from pygame import Rect
import pygame
from colors import darken_color
from colors.palette import BLACK, WHITE, GRAY

class Skill:
  PADDING_X = 6
  PADDING_Y = 5
  ICON_MARGIN = 9

  def render(skill, selected=True):
    assets = use_assets()
    icon = Skill.get_icon(skill)
    icon_bgcolor = skill.color
    icon_bgcolor = icon_bgcolor if selected else darken_color(icon_bgcolor)
    text_color = WHITE if selected else GRAY
    font = assets.fonts["standard"]
    sprite = assets.sprites["skill"]

    icon = recolor(icon, WHITE)
    icon = outline(icon, BLACK)
    text = render_text(skill.name, font)
    text = recolor(text, WHITE)

    surface = sprite.copy()
    pygame.draw.rect(surface, icon_bgcolor, Rect(3, 4, 16, 11))
    pygame.draw.rect(surface, icon_bgcolor, Rect(4, 3, 14, 13))
    surface.blit(icon, (Skill.PADDING_X, Skill.PADDING_Y))
    surface.blit(text, (
      Skill.PADDING_X + icon.get_width() + Skill.ICON_MARGIN,
      Skill.PADDING_Y + 1
    ))
    surface = replace_color(surface, WHITE, text_color)
    return surface

  def get_icon(skill):
    assets = use_assets()

    if skill.element == "sword":
      return assets.sprites["icon_sword"]
    elif skill.element == "lance":
      return assets.sprites["icon_lance"]
    elif skill.element == "axe":
      return assets.sprites["icon_axe"]
    elif skill.element == "shield":
      return assets.sprites["icon_shield"]
    elif skill.element == "fire":
      return assets.sprites["icon_fire"]
    elif skill.element == "ice":
      return assets.sprites["icon_ice"]
    elif skill.element == "volt":
      return assets.sprites["icon_volt"]
    elif skill.element == "wind":
      return assets.sprites["icon_wind"]
    elif skill.element == "dark":
      return assets.sprites["icon_skull"]

    if skill.kind == "magic":
      return assets.sprites["icon_hat"]
    elif skill.kind == "support":
      return assets.sprites["icon_skill"]
    elif skill.kind == "ailment":
      return assets.sprites["icon_skull"]
    elif skill.kind == "field":
      return assets.sprites["icon_skill"]
    elif skill.kind == "armor":
      return assets.sprites["icon_heartplus"]

    return None
