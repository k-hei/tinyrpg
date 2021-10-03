from dataclasses import dataclass
import pygame
from pygame import Surface, Rect, SRCALPHA
from assets import load as use_assets
from config import WINDOW_WIDTH
from colors.palette import BLACK, BLUE
from lib.filters import replace_color
from anims.tween import TweenAnim

class EnterAnim(TweenAnim): pass
class ExitAnim(TweenAnim): pass

@dataclass
class BannerControls:
  a: str = None
  b: str = None
  x: str = None
  y: str = None
  l: str = None
  r: str = None
  select: str = None
  start: str = None
  esc: str = None

class Banner:
  PADDING_X = 16
  PADDING_Y = 6
  MARGIN = 12
  SPACING_TEXT = 5
  SPACING_ICON = 12
  FONT_NAME = "normal"

  def render(**controls):
    assets = use_assets()
    font = assets.ttf[Banner.FONT_NAME]

    banner_width = WINDOW_WIDTH
    banner_height = font.get_size() + Banner.PADDING_Y * 2
    banner_image = Surface((banner_width, banner_height), SRCALPHA)
    banner_image.fill(BLACK)

    x = banner_width - Banner.PADDING_X
    for button, action in reversed(controls.items()):
      text_image = font.render(action)
      x -= text_image.get_width()
      y = Banner.PADDING_Y
      banner_image.blit(text_image, (x, y))
      icon_image = assets.sprites["button_" + button]
      icon_image = replace_color(icon_image, BLACK, BLUE)
      x -= Banner.SPACING_TEXT + icon_image.get_width()
      y = banner_height // 2 - icon_image.get_height() // 2 - 1
      banner_image.blit(icon_image, (x, y))
      x -= Banner.SPACING_ICON

    return banner_image

  def __init__(banner, **controls):
    BannerControls(**controls)
    banner.controls = controls
    banner.surface = None
    banner.anim = None
    banner.active = False

  def init(banner):
    banner.surface = Banner.render(**banner.controls)

  def enter(banner):
    banner.anim = TweenAnim(duration=6)
    banner.active = True

  def exit(banner):
    banner.anim = TweenAnim(duration=4)
    banner.active = False

  def draw(banner, surface):
    banner_image = banner.surface
    y = surface.get_height() - banner.MARGIN - banner_image.get_height()
    anim = banner.anim
    if anim:
      if anim.done:
        banner.anim = None
      anim.update()
      t = anim.pos
      if type(anim) is ExitAnim:
        t = 1 - t
      height = banner_image.get_height() * t
      y += banner_image.get_height() // 2 - height // 2
      pygame.draw.rect(surface, BLACK, Rect(0, y, WINDOW_WIDTH, height))
    elif banner.active:
      surface.blit(banner_image, (0, y))
