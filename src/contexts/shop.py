from math import sin, cos, pi
import pygame
from pygame import Rect
from pygame.transform import rotate, scale
from contexts import Context
from contexts.cardgroup import CardContext
from contexts.sell import SellContext
from cores.knight import KnightCore
from comps.control import Control
from comps.textbubble import TextBubble
from comps.card import Card
from hud import Hud
from assets import load as use_assets
from filters import replace_color, darken
from palette import BLACK, WHITE, RED, BLUE, BLUE_DARK, GOLD
import keyboard
from anims import Anim
from anims.tween import TweenAnim
from easing.expo import ease_out
from easing.circ import ease_out as ease_out_circ
from lib.lerp import lerp
from portraits.mira import MiraPortrait

class CursorAnim(Anim): blocking = False
class BackgroundEnterAnim(TweenAnim): blocking = True
class PortraitEnterAnim(TweenAnim): blocking = True

class TitleAnim(TweenAnim): blocking = True
class TitleEnterAnim(TitleAnim): pass
class TitleSlideAnim(TitleAnim): pass
class TitleSlideinAnim(TitleSlideAnim): pass
class TitleSlideoutAnim(TitleSlideAnim): pass

class SubtitleAnim(TweenAnim): blocking = True
class SubtitleEnterAnim(SubtitleAnim): pass
class SubtitleSlideAnim(SubtitleAnim): pass

def animate_text(anim, text, period, stagger=1, delay=0):
  anims = []
  for i, char in enumerate(text):
    anims.append(anim(
      duration=period,
      delay=i * stagger + delay,
      target=i
    ))
  return anims

class ShopContext(Context):
  title = "Fortune House"
  subtitle = "Destiny written in starlight"

  def __init__(ctx, items):
    super().__init__()
    ctx.items = items
    ctx.hero = KnightCore()
    ctx.portraits = [MiraPortrait()]
    ctx.messages = [
      "MIRA: What can I do you for...?",
      "MIRA: Need anything else...?"
    ]
    ctx.message_index = 0
    ctx.title_exiting = False
    ctx.subtitle_exiting = False
    ctx.hud = Hud()
    ctx.anims = [CursorAnim()]
    ctx.bubble = TextBubble(width=96, pos=(128, 40))
    ctx.controls = [
      Control(key=("X"), value="Menu")
    ]

  def enter(ctx):
    ctx.anims += [
      *animate_text(anim=TitleEnterAnim, text=ctx.title, period=5, stagger=3, delay=135),
      *animate_text(anim=SubtitleEnterAnim, text=ctx.subtitle, period=3, stagger=1, delay=90),
      SubtitleSlideAnim(duration=15, delay=len(ctx.subtitle) + 95),
      BackgroundEnterAnim(duration=15, delay=5),
      PortraitEnterAnim(
        duration=20,
        delay=30,
        on_end=ctx.focus
      )
    ]

  def message(ctx):
    return ctx.messages[ctx.message_index]

  def next_message(ctx):
    ctx.message_index = min(ctx.message_index + 1, len(ctx.messages) - 1)

  def focus(ctx):
    portrait = ctx.portraits[0]
    portrait.start_talk()
    ctx.bubble.print(ctx.message(), on_end=lambda: (
      portrait.stop_talk(),
      ctx.child is None and ctx.open(
        CardContext(pos=(16, 144), on_choose=ctx.handle_choose)
      )
    ))
    ctx.next_message()
    if ctx.child:
      ctx.child.focus()
      ctx.anims.append(TitleSlideinAnim(duration=12))
      ctx.title_exiting = False

  def handle_choose(ctx, card):
    if card.name == "buy": return
    if card.name == "sell": ctx.handle_sell(card)
    if card.name == "exit": return

  def handle_sell(ctx, card):
    ctx.anims.append(TitleSlideoutAnim(duration=7))
    ctx.title_exiting = True
    ctx.child.open(SellContext(
      items=ctx.items,
      bubble=ctx.bubble,
      portrait=ctx.portraits[0],
      card=card,
      on_close=ctx.focus
    ))

  def update(ctx):
    super().update()
    for anim in ctx.anims:
      if anim.done:
        ctx.anims.remove(anim)
      else:
        anim.update()

  def draw(ctx, surface):
    assets = use_assets()
    surface.fill(WHITE)
    pygame.draw.rect(surface, BLACK, Rect(0, 0, 256, 224))

    bg_image = assets.sprites["fortune_bg"]
    bg_image = replace_color(bg_image, WHITE, BLUE_DARK)
    bg_anim = next((a for a in ctx.anims if type(a) is BackgroundEnterAnim), None)
    if bg_anim:
      t = bg_anim.pos
      if t < 0.5:
        t = t / 0.5
        bg_width = int(bg_image.get_width() * t)
        bg_height = 4
      else:
        t = (t - 0.5) / 0.5
        bg_width = bg_image.get_width()
        bg_height = int(bg_image.get_height() * t)
      bg_image = scale(bg_image, (bg_width, bg_height))
    surface.blit(bg_image, (
      surface.get_width() / 2 - bg_image.get_width() / 2,
      128 / 2 - bg_image.get_height() / 2
    ))

    for portrait in ctx.portraits:
      portrait_image = portrait.render()
      portrait_x = surface.get_width() - portrait_image.get_width()
      portrait_y = 0
      portrait_anim = next((a for a in ctx.anims if type(a) is PortraitEnterAnim), None)
      if portrait_anim:
        t = ease_out_circ(portrait_anim.pos)
        portrait_x = lerp(surface.get_width(), portrait_x, t)
      surface.blit(portrait_image, (portrait_x, portrait_y))

    MARGIN = 2

    ctx.bubble.draw(surface)

    hud_image = ctx.hud.update(ctx.hero)
    hud_x = MARGIN
    hud_y = surface.get_height() - hud_image.get_height() - MARGIN
    surface.blit(hud_image, (hud_x, hud_y))

    if (not ctx.child
    or ctx.child.child is None
    or next((a for a in ctx.anims if (
      isinstance(a, TitleAnim)
      or isinstance(a, SubtitleAnim)
    )), None)):
      title_text = ctx.title
      title_font = assets.ttf["english_large"]
      title_width, title_height = title_font.size(title_text)
      title_x = surface.get_width() - title_width - 8
      title_y = surface.get_height() - title_height - 7
      title_anim = next((a for a in ctx.anims if isinstance(a, TitleSlideAnim)), None)
      if title_anim:
        t = title_anim.pos
        from_y = title_y + 48
        to_y = title_y
        if type(title_anim) is TitleSlideinAnim:
          t = ease_out(t)
        if type(title_anim) is TitleSlideoutAnim:
          t = 1 - t
        title_y = lerp(from_y, to_y, t)
      if title_anim or not ctx.title_exiting:
        char_x = title_x
        char_y = title_y
        for i, char in enumerate(title_text):
          char_anim = next((a for a in ctx.anims if type(a) is TitleEnterAnim and a.target == i), None)
          if char_anim:
            t = char_anim.pos
            c = int(0xFF * t)
            char_offset = (1 - ease_out(t)) * 12
            char_color = (c << 16) + (c << 8) + c
          else:
            char_offset = 0
            char_color = WHITE
          char_image = title_font.render(char, char_color)
          surface.blit(char_image, (char_x + char_offset, char_y + char_offset))
          char_x += char_image.get_width()

      subtitle_text = ctx.subtitle
      subtitle_font = assets.ttf["roman"]
      subtitle_width, subtitle_height = subtitle_font.size(subtitle_text)
      subtitle_x = title_x + title_width - subtitle_width
      subtitle_y = title_y - title_height + 2
      subtitle_anim = next((a for a in ctx.anims if type(a) is SubtitleSlideAnim), None)
      if subtitle_anim:
        t = subtitle_anim.pos
        if type(subtitle_anim) is SubtitleSlideAnim:
          t = ease_out(t)
          subtitle_y = lerp(surface.get_height() - subtitle_height - 7, subtitle_y, t)
      if subtitle_anim or not ctx.subtitle_exiting:
        char_x = subtitle_x
        char_y = subtitle_y
        for i, char in enumerate(subtitle_text):
          char_anim = next((a for a in ctx.anims if type(a) is SubtitleEnterAnim and a.target == i), None)
          if char_anim:
            t = char_anim.pos
            c = int(0xFF * t)
            char_offset = (1 - ease_out(t)) * 12
            char_color = (c << 16) + (c << 8) + c
          else:
            char_offset = 0
            char_color = WHITE
          char_image = subtitle_font.render(char, char_color)
          surface.blit(char_image, (char_x + char_offset, char_y + char_offset))
          char_x += char_image.get_width()

    if type(ctx.child) is CardContext:
      sprites = ctx.child.view()
      for sprite in sprites:
        sprite.draw(surface)
    elif ctx.child:
      ctx.child.draw(surface)
