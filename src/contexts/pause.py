import pygame
from pygame import Surface, Color, SRCALPHA
from pygame.transform import flip

import keyboard
from contexts import Context
from assets import load as use_assets
from filters import outline, recolor, replace_color
from colors.palette import WHITE, BLUE, BLACK, GOLD
from config import WINDOW_SIZE, WINDOW_HEIGHT
from comps.hud import Hud
from comps.previews import Previews
from comps.minimap import Minimap
from comps.spmeter import SpMeter
from comps.floorno import FloorNo
from sprite import Sprite

MARGIN_X = 48
MARGIN_Y = 48
SPACING = 4
GOLD_SPACING = 4
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

  def view(ctx):
    sprites = []
    assets = use_assets()

    # tint
    tint = Surface(WINDOW_SIZE, SRCALPHA)
    tint.fill(Color(0, 0, 0, 0x7F))
    sprites.append(Sprite(
      image=tint,
      pos=(0, 0)
    ))

    # gold
    gold_image = assets.sprites["item_gold"]
    gold_image = replace_color(gold_image, BLACK, GOLD)
    gold_x = MARGIN_X
    gold_y = WINDOW_HEIGHT - MARGIN_Y
    sprites.append(Sprite(
      image=gold_image,
      pos=(gold_x, gold_y)
    ))

    gold_amount = ctx.parent.get_gold()
    gold_text = assets.ttf["english"].render("{}G".format(gold_amount))
    gold_x += gold_image.get_width() + GOLD_SPACING
    gold_y += gold_image.get_height() // 2 - gold_text.get_height() // 2
    sprites.append(Sprite(
      image=gold_text,
      pos=(gold_x, gold_y)
    ))

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
      sprites.append(Sprite(
        image=text_image,
        pos=(x, y)
      ))

    # hand
    hand_image = flip(assets.sprites["hand"], True, False)
    hand_x = MARGIN_X - hand_image.get_width() - HAND_SPACING
    hand_y = MARGIN_Y
    sprites.append(Sprite(
      image=hand_image,
      pos=(hand_x, hand_y)
    ))

    # hud
    hud_image = assets.sprites["hud_single"]
    hud_x = MARGIN_X + choices_width + HUD_MARGIN
    hud_y = MARGIN_Y
    sprites += [
      Sprite(image=hud_image, pos=(hud_x, hud_y)),
      Sprite(image=assets.sprites["circle_knight"], pos=(hud_x, hud_y + 1))
    ]

    hud_y += hud_image.get_height() + HUD_MARGIN
    sprites += [
      Sprite(image=hud_image, pos=(hud_x, hud_y)),
      Sprite(image=assets.sprites["circle_mage"], pos=(hud_x, hud_y + 1))
    ]

    return sprites
