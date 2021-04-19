from assets import load as use_assets
from text import render as render_text
from filters import recolor, outline, replace_color
from pygame import Rect
import pygame
import palette

class Skill:
  PADDING_X = 6
  PADDING_Y = 5
  ICON_MARGIN = 9

  def render(skill, selected=True):
    assets = use_assets()
    icon = Skill.get_icon(skill)
    icon_bgcolor = Skill.get_color(skill)
    icon_bgcolor = icon_bgcolor if selected else palette.darken(icon_bgcolor)
    text_color = (0xFF, 0xFF, 0xFF) if selected else (0x7F, 0x7F, 0x7F)
    font = assets.fonts["standard"]
    sprite = assets.sprites["skill"]

    icon = recolor(icon, (0xFF, 0xFF, 0xFF))
    icon = outline(icon, (0x00, 0x00, 0x00))
    text = render_text(skill.name, font)
    text = recolor(text, palette.WHITE)

    surface = sprite.copy()
    pygame.draw.rect(surface, icon_bgcolor, Rect(3, 4, 16, 11))
    pygame.draw.rect(surface, icon_bgcolor, Rect(4, 3, 14, 13))
    surface.blit(icon, (Skill.PADDING_X, Skill.PADDING_Y))
    surface.blit(text, (
      Skill.PADDING_X + icon.get_width() + Skill.ICON_MARGIN,
      Skill.PADDING_Y + 1
    ))
    surface = replace_color(surface, palette.WHITE, text_color)
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

    if skill.kind == "magic":
      return assets.sprites["icon_hat"]
    elif skill.kind == "support":
      return assets.sprites["icon_skill"]
    elif skill.kind == "ailment":
      return assets.sprites["icon_skull"]
    elif skill.kind == "field":
      return assets.sprites["icon_skill"]
    elif skill.kind == "passive":
      return assets.sprites["icon_heartplus"]

    return None

  def get_color(skill):
    assets = use_assets()
    if skill.kind == "attack":
      return palette.RED
    elif skill.kind == "magic":
      return palette.BLUE
    elif skill.kind == "support":
      return palette.GREEN
    elif skill.kind == "ailment":
      return palette.PURPLE
    elif skill.kind == "field":
      return palette.YELLOW
    elif skill.kind == "passive":
      return palette.YELLOW
