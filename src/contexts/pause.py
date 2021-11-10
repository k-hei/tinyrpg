import pygame
from pygame import Surface, Color, SRCALPHA
from pygame.transform import flip, rotate
import lib.keyboard as keyboard
import lib.gamepad as gamepad
from lib.sprite import Sprite
from lib.filters import outline, replace_color, shadow_lite as shadow
from lib.animstep import step_anims
from easing.expo import ease_out
import assets

from contexts import Context
from anims import Anim
from anims.sine import SineAnim
from anims.tween import TweenAnim
from colors import darken_color
from colors.palette import BLACK, WHITE, BLUE, VIOLET, GREEN, SAFFRON, RED, GRAY, GOLD
from config import WINDOW_SIZE, WINDOW_HEIGHT

MARGIN_X = 48
MARGIN_Y = 32
OPTION_SPACING = 4
OPTION_OFFSET = 32
GOLD_SPACING = 4
HAND_OFFSET = 4
HUD_MARGIN = 8

class CursorAnim(SineAnim):
  period = 30
  amplitude = 2

class OptionSquare:
  class SpinAnim(Anim): pass
  class EnterAnim(TweenAnim): duration = 15
  class ExitAnim(TweenAnim): duration = 8

  def __init__(square, y):
    square.y = y
    square.anims = [OptionSquare.SpinAnim(), OptionSquare.EnterAnim()]
    square.exiting = False
    square.done = False

  def exit(square):
    square.exiting = True
    square.anims.append(OptionSquare.ExitAnim(on_end=lambda: (
      setattr(square, "done", True)
    )))

  def update(square):
    if square.done:
      return
    square.anims = step_anims(square.anims)

  def view(square):
    square_image = assets.sprites["pause_square"]
    square_scale = 1
    square_angle = 0

    enter_anim = next((a for a in square.anims if type(a) is OptionSquare.EnterAnim), None)
    exit_anim = next((a for a in square.anims if type(a) is OptionSquare.ExitAnim), None)
    if enter_anim:
      t = ease_out(enter_anim.pos)
      square_scale *= t
      square_angle -= t * 360 * 0.75
    elif exit_anim:
      square_scale *= 1 - exit_anim.pos

    spin_anim = next((a for a in square.anims if type(a) is OptionSquare.SpinAnim), None)
    if spin_anim:
      square_angle -= spin_anim.time
      square_image = rotate(square_image, square_angle % 360)

    return [Sprite(
      image=square_image,
      origin=Sprite.ORIGIN_CENTER,
      size=(square_image.get_width() * square_scale, square_image.get_height() * square_scale)
    )]

class PauseContext(Context):
  choices = ["item", "equip", "status", "quest", "monster", "option"]
  choice_colors = [BLUE, VIOLET, GREEN, SAFFRON, RED, GRAY]

  def __init__(ctx, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.cursor_index = 0
    ctx.cursor_drawn = 0
    ctx.choices_xs = { 0: OPTION_OFFSET }
    ctx.anims = [CursorAnim()]
    ctx.comps = [OptionSquare(y=0)]

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
    new_index = ctx.cursor_index + delta
    if new_index < 0:
      return False
    if new_index > len(ctx.choices) - 1:
      return False
    square = next((a for a in ctx.comps if type(a) is OptionSquare and a.y == ctx.cursor_index), None)
    square and square.exit()
    ctx.cursor_index = new_index
    ctx.comps.append(OptionSquare(y=new_index))
    return True

  def update(ctx):
    ctx.anims = step_anims(ctx.anims)
    ctx.comps = step_anims(ctx.comps)
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
      text_image = assets.ttf["roman_large"].render(text, WHITE if i == ctx.cursor_index else GRAY)
      text_image = outline(text_image, BLACK)
      text_image = shadow(text_image, BLACK)
      if text_image.get_width() > choices_width:
        choices_width = text_image.get_width()
      if i not in ctx.choices_xs:
        ctx.choices_xs[i] = 0
      option_x = MARGIN_X + ctx.choices_xs[i]
      option_y = i * (text_image.get_height() + OPTION_SPACING) + MARGIN_Y
      option_image = assets.sprites["pause_option"]
      if i == ctx.cursor_index:
        ctx.choices_xs[i] += (OPTION_OFFSET - ctx.choices_xs[i]) / 4
        option_image = replace_color(option_image, WHITE, ctx.choice_colors[i])
      else:
        ctx.choices_xs[i] += -ctx.choices_xs[i] / 4
        option_image = replace_color(option_image, WHITE, darken_color(ctx.choice_colors[i]))
      sprites += [Sprite(
        image=option_image,
        pos=(0, option_y),
      ), Sprite(
        image=text_image,
        pos=(option_x, option_y)
      )]

    selection_y = ctx.cursor_index * (text_image.get_height() + OPTION_SPACING)

    # hand
    hand_image = flip(assets.sprites["hand"], True, False)
    hand_x = MARGIN_X - hand_image.get_width() + HAND_OFFSET
    hand_y = MARGIN_Y + selection_y
    hand_anim = next((a for a in ctx.anims if isinstance(a, CursorAnim)), None)
    if hand_anim:
      hand_x += hand_anim.pos
    sprites.append(Sprite(
      image=hand_image,
      pos=(hand_x, hand_y)
    ))

    for comp in ctx.comps:
      comp_y = comp.y * (text_image.get_height() + OPTION_SPACING)
      sprites += Sprite.move_all(
        sprites=comp.view(),
        offset=(MARGIN_X + 14, MARGIN_Y + comp_y + text_image.get_height() / 2),
      )

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
