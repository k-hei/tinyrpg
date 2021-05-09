import pygame
from pygame import Surface
from pygame.transform import flip

import keyboard
from contexts import Context
from assets import load as use_assets
from filters import outline, recolor
from palette import WHITE, BLUE
from comps.hud import Hud
from comps.previews import Previews
from comps.minimap import Minimap
from comps.spmeter import SpMeter
from comps.floorno import FloorNo

MARGIN_X = 48
MARGIN_Y = 48
SPACING = 4
HAND_SPACING = 4
HUD_MARGIN = 8

class PauseContext(Context):
  choices = ["item", "equip", "status", "quest", "option"]
  effects = [Hud, Previews, Minimap, SpMeter, FloorNo]

  def __init__(ctx, parent=None, on_close=None):
    super().__init__(parent, on_close)

  def handle_keydown(ctx, key):
    if keyboard.get_pressed(key) > 1:
      return False
    if key == pygame.K_ESCAPE:
      return ctx.close()

  def draw(ctx, surface):
    assets = use_assets()

    # tint
    tint = Surface(surface.get_size(), pygame.SRCALPHA)
    tint.fill(0x7F000000)
    surface.blit(tint, (0, 0))

    # choices
    choices_width = 0
    for i, choice in enumerate(ctx.choices):
      text = choice.upper()
      text_image = assets.ttf["special"].render(text, WHITE)
      text_image = outline(text_image, BLUE)
      if text_image.get_width() > choices_width:
        choices_width = text_image.get_width()
      x = MARGIN_X
      y = i * (text_image.get_height() + SPACING) + MARGIN_Y
      surface.blit(text_image, (x, y))

    # hand
    hand_image = flip(assets.sprites["hand"], True, False)
    hand_x = MARGIN_X - hand_image.get_width() - HAND_SPACING
    hand_y = MARGIN_Y
    surface.blit(hand_image, (hand_x, hand_y))

    # hud
    hud_image = assets.sprites["hud_single"]
    hud_x = MARGIN_X + choices_width + HUD_MARGIN
    hud_y = MARGIN_Y
    surface.blit(hud_image, (hud_x, hud_y))
    surface.blit(assets.sprites["circle_knight"], (hud_x, hud_y + 1))

    hud_y += hud_image.get_height() + HUD_MARGIN
    surface.blit(hud_image, (hud_x, hud_y))
    surface.blit(assets.sprites["circle_mage"], (hud_x, hud_y + 1))
