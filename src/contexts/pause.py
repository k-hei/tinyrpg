import pygame
from pygame import Surface, Color, SRCALPHA
from pygame.transform import flip
import lib.keyboard as keyboard
import lib.gamepad as gamepad
from lib.sprite import Sprite
from lib.filters import outline, replace_color
import assets

from contexts import Context
from anims.sine import SineAnim
from colors.palette import WHITE, BLUE, DARKBLUE, BLACK, GOLD
from config import WINDOW_SIZE, WINDOW_HEIGHT

MARGIN_X = 48
MARGIN_Y = 32
OPTION_SPACING = 4
GOLD_SPACING = 4
HAND_SPACING = 4
HUD_MARGIN = 8

class CursorAnim(SineAnim):
  period = 30
  amplitude = 2

class PauseContext(Context):
  choices = ["item", "equip", "status", "quest", "monster", "option"]

  def __init__(ctx, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.cursor_index = 0
    ctx.cursor_drawn = 0
    ctx.anims = [CursorAnim()]

  def handle_press(ctx, key):
    if keyboard.get_state(key) + gamepad.get_state(key) > 1:
      return False
    if key in (pygame.K_UP, gamepad.controls.UP):
      return ctx.handle_move(delta=-1)
    if key in (pygame.K_DOWN, gamepad.controls.DOWN):
      return ctx.handle_move(delta=1)
    if key == pygame.K_ESCAPE:
      return ctx.close()

  def handle_move(ctx, delta):
    if ctx.cursor_index + delta < 0:
      return False
    if ctx.cursor_index + delta < 0:
      return False
    ctx.cursor_index += delta
    return True

  def update(ctx):
    ctx.anims = [(a.update(), a)[-1] for a in ctx.anims if not a.done]
    ctx.cursor_drawn += (ctx.cursor_index - ctx.cursor_drawn) / 4

  def view(ctx):
    sprites = []

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

    game = ctx.get_parent(cls="GameContext")
    if game:
      gold_amount = game.store.gold
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
      text = choice[0].upper() + choice[1:]
      text_image = assets.ttf["roman_large"].render(text, WHITE)
      text_image = outline(text_image, BLACK)
      if text_image.get_width() > choices_width:
        choices_width = text_image.get_width()
      option_x = MARGIN_X
      option_y = i * (text_image.get_height() + OPTION_SPACING) + MARGIN_Y
      option_image = assets.sprites["pause_option"]
      option_image = replace_color(option_image, WHITE, BLUE if i == ctx.cursor_index else DARKBLUE)
      sprites += [Sprite(
        image=option_image,
        pos=(0, option_y),
      ), Sprite(
        image=text_image,
        pos=(option_x, option_y)
      )]

    # hand
    hand_image = flip(assets.sprites["hand"], True, False)
    hand_x = MARGIN_X - hand_image.get_width() - HAND_SPACING
    hand_y = MARGIN_Y + ctx.cursor_drawn * (text_image.get_height() + OPTION_SPACING)
    hand_anim = next((a for a in ctx.anims if isinstance(a, CursorAnim)), None)
    if hand_anim:
      hand_x += hand_anim.pos
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
    ]

    hud_y += hud_image.get_height() + HUD_MARGIN
    sprites += [
      Sprite(image=hud_image, pos=(hud_x, hud_y)),
    ]

    return [sprites]
