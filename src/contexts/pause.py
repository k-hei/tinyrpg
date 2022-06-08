from copy import deepcopy
import pygame
from pygame import Surface, Color, SRCALPHA
from pygame.transform import flip, rotate
import lib.input as input
import lib.vector as vector
from lib.sprite import Sprite
from lib.filters import stroke, outline, replace_color, recolor, shadow_lite as shadow
from lib.animstep import step_anims
from lib.lerp import lerp
from text import render as render_text
from easing.expo import ease_out
import assets

from contexts import Context
from contexts.inventory import InventoryContext
from contexts.custom import CustomContext
from comps.goldbubble import GoldBubble
from comps.hud import Hud
from comps.textbox import TextBox
from anims import Anim
from anims.sine import SineAnim
from anims.tween import TweenAnim
from anims.walk import WalkAnim
from colors import darken_color
from colors.palette import BLACK, WHITE, BLUE, VIOLET, GREEN, SAFFRON, RED, GRAY, GOLD, ORANGE
from config import WINDOW_SIZE, WINDOW_WIDTH

XMARGIN = 48
YMARGIN = 32
OPTION_SPACING = 4
OPTION_OFFSET = 28
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
    square.icon = stroke(icon, BLACK)
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

class ChoiceStrip:
  class EnterAnim(TweenAnim): duration = 15
  class ExitAnim(TweenAnim): duration = 8
  class SelectAnim(TweenAnim): duration = 8
  class DeselectAnim(TweenAnim): duration = 8

  def __init__(choice, color, delay=0):
    choice.color = color
    choice.delay = delay
    choice.selected = False
    choice.done = False
    choice.exiting = False
    choice.anims = []
    choice.enter()

  def enter(choice):
    choice.anims = [ChoiceStrip.EnterAnim(delay=choice.delay)]
    choice.cache_selected = assets.sprites["pause_option_selected"]
    choice.cache_selected = replace_color(choice.cache_selected, WHITE, choice.color)
    choice.cache_selected = stroke(choice.cache_selected, BLACK)
    choice.cache_deselected = assets.sprites["pause_option"]
    choice.cache_deselected = replace_color(choice.cache_deselected, WHITE, darken_color(choice.color))
    choice.cache_deselected = stroke(choice.cache_deselected, BLACK)

  def select(choice):
    choice.selected = True
    choice.anims.append(ChoiceStrip.SelectAnim())

  def deselect(choice):
    choice.selected = False
    choice.anims.append(ChoiceStrip.DeselectAnim())

  def update(choice):
    choice_anim = choice.anims[0] if choice.anims else None
    if choice_anim:
      choice_anim.update()
      if choice_anim.done:
        choice.anims.pop(0)

  def view(choice):
    choice_image = choice.cache_deselected
    choice_y = choice_image.get_height() / 2
    choice_anim = choice.anims[0] if choice.anims else None
    if type(choice_anim) is not ChoiceStrip.EnterAnim and (
      choice.selected
      or type(choice_anim) in (ChoiceStrip.SelectAnim, ChoiceStrip.DeselectAnim)
    ):
      choice_image = choice.cache_selected
      choice_y = choice_image.get_height() / 4

    choice_x = -1
    if type(choice_anim) is ChoiceStrip.EnterAnim:
      t = ease_out(choice_anim.pos)
      choice_x = lerp(-choice_image.get_width(), choice_x, t)

    choice_height = choice_image.get_height()
    if type(choice_anim) is ChoiceStrip.SelectAnim:
      choice_height = lerp(
        a=choice.cache_deselected.get_height(),
        b=choice.cache_selected.get_height(),
        t=ease_out(choice_anim.pos)
      )
      choice_y = choice_height / 4
      choice_x = lerp(
        a=-(choice.cache_selected.get_width() - choice.cache_deselected.get_width()),
        b=choice_x,
        t=ease_out(choice_anim.pos)
      )
    elif type(choice_anim) is ChoiceStrip.DeselectAnim:
      choice_height = lerp(
        a=choice_height,
        b=choice.cache_deselected.get_height(),
        t=choice_anim.pos
      )
      choice_y = choice_height / 4
      choice_x = lerp(
        a=choice_x,
        b=-(choice.cache_selected.get_width() - choice.cache_deselected.get_width()),
        t=choice_anim.pos
      )

    return [Sprite(
      image=choice_image,
      pos=(choice_x, choice_y),
      origin=Sprite.ORIGIN_LEFT,
      size=(choice_image.get_width(), choice_height),
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
    ctx.choice_strips = [ChoiceStrip(color=c, delay=i * 5) for i, c in enumerate(ctx.choice_colors)]
    ctx.choice_text_xs = { 0: OPTION_OFFSET }
    ctx.anims = [CursorAnim()]
    ctx.comps = [IconSquare(y=0, icon=PauseContext.find_icon(0))]
    ctx.huds = [Hud(party=[c], hp=True, portrait=False) for c in store.party]
    ctx.party = deepcopy(store.party)
    ctx.goldbubble = GoldBubble(gold=store.gold)
    ctx.textbox = TextBox(size=(112, 20), color=WHITE)

  def enter(ctx):
    ctx.textbox.print(ctx.choice_descs[0])
    ctx.party_facings = { i: char.facing for (i, char) in enumerate(ctx.party) }
    for char in ctx.party:
      char.anims = [WalkAnim(period=30)]
      char.facing = (0, 1)
    ctx.choice_strips[0].select()

  def exit(ctx):
    for i, char in enumerate(ctx.party):
      char.anims = []
      char.facing = ctx.party_facings[i]
    ctx.close()
    return True

  def handle_press(ctx, button):
    if input.get_state(button) > 1:
      return False

    controls = input.resolve_controls(button)
    button = input.resolve_button(button)
    if button == input.BUTTON_UP:
      return ctx.handle_move(delta=-1)
    if button == input.BUTTON_DOWN:
      return ctx.handle_move(delta=1)

    for control in controls:
      if control == input.CONTROL_CONFIRM:
        return ctx.handle_choose()
      if control == input.CONTROL_CANCEL:
        return ctx.exit()

  def handle_move(ctx, delta):
    new_index = ctx.cursor_index + delta
    if new_index < 0:
      return False
    if new_index > len(ctx.choices) - 1:
      return False
    square = next((a for a in ctx.comps if type(a) is IconSquare and a.y == ctx.cursor_index), None)
    square and square.exit()
    ctx.choice_strips[ctx.cursor_index].deselect()
    ctx.cursor_index = new_index
    ctx.comps.append(IconSquare(y=new_index, icon=PauseContext.find_icon(new_index)))
    ctx.choice_strips[ctx.cursor_index].select()
    ctx.textbox.print(ctx.choice_descs[new_index])
    return True

  def handle_choose(ctx):
    choice = ctx.choices[ctx.cursor_index]
    if choice == "item":
      ctx.close()
      ctx.parent.open(InventoryContext(store=ctx.store))
    elif choice == "equip":
      ctx.close()
      ctx.parent.open(CustomContext(store=ctx.store), on_close=lambda: (
        ctx.store.update_skills()
      ))

  def update(ctx):
    ctx.anims = step_anims(ctx.anims)
    ctx.comps = step_anims(ctx.comps)
    ctx.choice_strips = step_anims(ctx.choice_strips)
    ctx.cursor_drawn += (ctx.cursor_index - ctx.cursor_drawn) / 2

    for char in ctx.party:
      char.update()

    for hud in ctx.huds:
      hud.update()

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
      is_choice_selected = i == ctx.cursor_index
      text = choice[0].upper() + choice[1:]
      text_image = assets.ttf["roman_large"].render(text, WHITE if is_choice_selected else GRAY)
      text_image = outline(text_image, BLACK)
      text_image = shadow(text_image, BLACK)
      if text_image.get_width() > choices_width:
        choices_width = text_image.get_width()
      if i not in ctx.choice_text_xs:
        ctx.choice_text_xs[i] = 0
      text_x = XMARGIN + ctx.choice_text_xs[i]

      if is_choice_selected:
        ctx.choice_text_xs[i] += (OPTION_OFFSET - ctx.choice_text_xs[i]) / 4
      else:
        ctx.choice_text_xs[i] += -ctx.choice_text_xs[i] / 4

      option_y = i * (text_image.get_height() + OPTION_SPACING) + YMARGIN
      option_view = ctx.choice_strips[i].view()
      sprites += Sprite.move_all(
        sprites=option_view,
        offset=(0, option_y)
      ) + [Sprite(
        image=text_image,
        pos=(text_x, option_y),
      )]

    selection_y = ctx.cursor_drawn * (text_image.get_height() + OPTION_SPACING)

    # icon square
    for comp in ctx.comps:
      comp_y = comp.y * (text_image.get_height() + OPTION_SPACING)
      sprites += Sprite.move_all(
        sprites=comp.view(),
        offset=(XMARGIN + 12, YMARGIN + comp_y + text_image.get_height() / 2),
      )

    # hand
    if not next((a for s in ctx.choice_strips for a in s.anims if type(a) is ChoiceStrip.EnterAnim), None):
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
    sprites += [desc_sprite := Sprite(
      image=outline(ctx.textbox.render(), BLACK),
      pos=(XMARGIN, YMARGIN + len(ctx.choices) * (text_image.get_height() + OPTION_SPACING) + 8),
    )]

    # gold
    sprites += Sprite.move_all(
      sprites=ctx.goldbubble.view(),
      offset=(WINDOW_WIDTH - XMARGIN, desc_sprite.rect.centery),
      origin=Sprite.ORIGIN_TOPRIGHT
    )

    # huds
    hud_x = XMARGIN + choices_width + HUD_XMARGIN
    hud_y = YMARGIN
    for i, hud in enumerate(ctx.huds):
      hud_image = hud.render(portrait=False)
      char = ctx.party[i]
      char_view = char.view()
      sprites += [
        Sprite(image=hud_image, pos=(hud_x, hud_y)),
        *(Sprite.move_all(
          sprites=char_view,
          offset=vector.add(
            (hud_x, hud_y - 2),
            vector.scale(assets.sprites["hud_circle"].get_size(), 1 / 2),
          ),
          origin=Sprite.ORIGIN_CENTER,
        ) if not char.dead else [])
      ]
      hud_y += hud_image.get_height() + HUD_YMARGIN

    return [sprites]
