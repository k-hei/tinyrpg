import pygame
from pygame import Surface, Color, SRCALPHA
from pygame.transform import flip, rotate
import lib.keyboard as keyboard
import lib.gamepad as gamepad
import lib.vector as vector
from lib.sprite import Sprite
from lib.filters import outline, replace_color, recolor, shadow_lite as shadow
from lib.animstep import step_anims
from text import render as render_text
from easing.expo import ease_out
import assets

from contexts import Context
from comps.hud import Hud
from comps.textbox import TextBox
from anims import Anim
from anims.sine import SineAnim
from anims.tween import TweenAnim
from colors import darken_color
from colors.palette import BLACK, WHITE, BLUE, VIOLET, GREEN, SAFFRON, RED, GRAY, GOLD, ORANGE
from config import WINDOW_SIZE

XMARGIN = 48
YMARGIN = 32
OPTION_SPACING = 4
OPTION_OFFSET = 26
GOLD_SPACING = 4
HAND_OFFSET = 4
HUD_XMARGIN = 32
HUD_YMARGIN = 8

class CursorAnim(SineAnim):
  period = 30
  amplitude = 2

class IconSquare:
  class SpinAnim(SineAnim): period = 90
  class EnterAnim(TweenAnim): duration = 15
  class ExitAnim(TweenAnim): duration = 8

  def __init__(square, y, icon):
    square.y = y
    square.icon = icon
    square.anims = [IconSquare.SpinAnim(), IconSquare.EnterAnim()]
    square.exiting = False
    square.done = False

  def exit(square):
    square.exiting = True
    square.anims.append(IconSquare.ExitAnim(on_end=lambda: (
      setattr(square, "done", True)
    )))

  def update(square):
    if square.done:
      return
    square.anims = step_anims(square.anims)

  def view(square):
    square_image = assets.sprites["pauseicon_square"]
    square_scale = 1
    square_angle = 0

    enter_anim = next((a for a in square.anims if type(a) is IconSquare.EnterAnim), None)
    exit_anim = next((a for a in square.anims if type(a) is IconSquare.ExitAnim), None)
    if enter_anim:
      t = ease_out(enter_anim.pos)
      square_scale *= t
      square_angle -= t * 360 * 0.75
    elif exit_anim:
      square_scale *= 1 - exit_anim.pos

    spin_anim = next((a for a in square.anims if type(a) is IconSquare.SpinAnim), None)
    if spin_anim:
      square_angle -= spin_anim.time
      square_image = rotate(square_image, square_angle % 360)

    icon_image = square.icon
    icon_y = -spin_anim.pos * 2 - 2

    return [Sprite(
      image=square_image,
      origin=Sprite.ORIGIN_CENTER,
      size=vector.scale(square_image.get_size(), square_scale)
    ), Sprite(
      image=icon_image,
      pos=(0, icon_y),
      origin=Sprite.ORIGIN_CENTER,
      size=vector.scale(icon_image.get_size(), square_scale)
    )]

class PauseContext(Context):
  choices = ["item", "equip", "status", "quest", "monster", "option"]
  choice_descs = [
    "Manage inventory and use items.",
    "Equip and arrange artifacts.",
    "View character stats and skills.",
    "View accepted and completed quests.",
    "View data on defeated enemies.",
    "View and change game settings.",
  ]
  choice_colors = [BLUE, VIOLET, GREEN, SAFFRON, RED, GRAY]
  icon_colors = [RED, GRAY, BLUE, ORANGE, RED, GRAY]

  def find_icon(index):
    icon_image = assets.sprites[f"pauseicon_{PauseContext.choices[index]}"]
    icon_image = replace_color(icon_image, BLACK, PauseContext.icon_colors[index])
    return icon_image

  def __init__(ctx, store, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.store = store
    ctx.cursor_index = 0
    ctx.cursor_drawn = 0
    ctx.choices_xs = { 0: OPTION_OFFSET }
    ctx.anims = [CursorAnim()]
    ctx.comps = [IconSquare(y=0, icon=PauseContext.find_icon(0))]
    ctx.huds = [Hud(party=[c], hp=True) for c in store.party]
    ctx.textbox = TextBox(size=(112, 20), color=WHITE)
    ctx.textbox.print(ctx.choice_descs[0])

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
    square = next((a for a in ctx.comps if type(a) is IconSquare and a.y == ctx.cursor_index), None)
    square and square.exit()
    ctx.cursor_index = new_index
    ctx.comps.append(IconSquare(y=new_index, icon=PauseContext.find_icon(new_index)))
    ctx.textbox.print(ctx.choice_descs[new_index])
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

    # title
    if ctx.anims[0].time % 60 < 45:
      title_image = render_text("PAUSED", assets.fonts["smallcaps"])
      title_image = recolor(title_image, GOLD)
      title_image = outline(title_image, BLACK)
      title_image = shadow(title_image, BLACK)
      sprites += [Sprite(
        image=title_image,
        pos=(XMARGIN, YMARGIN - 4),
        origin=Sprite.ORIGIN_BOTTOMLEFT,
      )]

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
      option_x = XMARGIN + ctx.choices_xs[i]
      option_y = i * (text_image.get_height() + OPTION_SPACING) + YMARGIN
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

    selection_y = ctx.cursor_drawn * (text_image.get_height() + OPTION_SPACING)

    # icon square
    for comp in ctx.comps:
      comp_y = comp.y * (text_image.get_height() + OPTION_SPACING)
      sprites += Sprite.move_all(
        sprites=comp.view(),
        offset=(XMARGIN + 10, YMARGIN + comp_y + text_image.get_height() / 2),
      )

    # hand
    hand_image = flip(assets.sprites["hand"], True, False)
    hand_x = XMARGIN - hand_image.get_width() + HAND_OFFSET
    hand_y = YMARGIN + selection_y
    hand_anim = next((a for a in ctx.anims if isinstance(a, CursorAnim)), None)
    if hand_anim:
      hand_x += hand_anim.pos
    sprites.append(Sprite(
      image=hand_image,
      pos=(hand_x, hand_y)
    ))

    # description
    sprites += [Sprite(
      image=outline(ctx.textbox.render(), BLACK),
      pos=(XMARGIN, YMARGIN + len(ctx.choices) * (text_image.get_height() + OPTION_SPACING) + 8),
    )]

    # huds
    hud_x = XMARGIN + choices_width + HUD_XMARGIN
    hud_y = YMARGIN
    for hud in ctx.huds:
      hud_image = hud.render()
      sprites += [
        Sprite(image=hud_image, pos=(hud_x, hud_y)),
      ]
      hud_y += hud_image.get_height() + HUD_YMARGIN

    return [sprites]
