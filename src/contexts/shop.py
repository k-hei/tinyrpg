from dataclasses import dataclass
from math import sin, cos, pi
import pygame
from pygame import Rect, Surface, Color
from pygame.transform import rotate, scale
from contexts import Context
from contexts.cardgroup import CardContext, CARD_BUY, CARD_SELL, CARD_EXIT
from contexts.buy import BuyContext
from contexts.sell import SellContext
from cores.knight import Knight
from comps.bg import Bg
from comps.box import Box
from comps.card import Card
from comps.control import Control
from comps.goldbubble import GoldBubble
from comps.hud import Hud
from comps.portraitgroup import PortraitGroup
from comps.textbox import TextBox
from comps.textbubble import TextBubble
import assets
from assets import load as use_assets
from lib.filters import replace_color, darken_image
from colors.palette import BLACK, WHITE, RED, BLUE, DARKBLUE, GOLD, ORANGE
import lib.keyboard as keyboard
from anims import Anim
from anims.tween import TweenAnim
from easing.expo import ease_out
from easing.circ import ease_out as ease_out_circ
from lib.lerp import lerp
from portraits import Portrait
from portraits.mira import MiraPortrait
from config import WINDOW_WIDTH, WINDOW_HEIGHT
from lib.sprite import Sprite
from transits.slide import SlideDown

BG_HEIGHT = 128
BOTTOMBAR_HEIGHT = WINDOW_HEIGHT - BG_HEIGHT

class CursorAnim(Anim): blocking = False
class HudEnterAnim(TweenAnim): blocking = True

class BackgroundAnim(TweenAnim): blocking = True
class BackgroundEnterAnim(BackgroundAnim): pass
class BackgroundExitAnim(BackgroundAnim): pass
class BackgroundSlideupAnim(TweenAnim): blocking = True

class PortraitAnim(TweenAnim): blocking = True
class PortraitEnterAnim(PortraitAnim): pass
class PortraitExitAnim(PortraitAnim): pass

class TitleAnim(TweenAnim): blocking = True
class TitleEnterAnim(TitleAnim): pass
class TitleSlideAnim(TitleAnim): pass
class TitleSlideinAnim(TitleSlideAnim): pass
class TitleSlideoutAnim(TitleSlideAnim): pass

class SubtitleAnim(TweenAnim): blocking = True
class SubtitleEnterAnim(SubtitleAnim): pass
class SubtitleSlideAnim(SubtitleAnim): pass

class BoxAnim(TweenAnim): blocking = True
class BoxEnterAnim(BoxAnim): pass
class BoxExitAnim(BoxAnim): pass

@dataclass
class ShopCard:
  name: str
  text: str
  portrait: Portrait = None

@dataclass
class ComponentStore:
  goldbubble: GoldBubble = None
  textbubble: TextBubble = None
  bagbubble: TextBubble = None
  portraitgroup: PortraitGroup = None
  hud: Hud = None
  card: Card = None

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
  def __init__(ctx, store, title, subtitle, messages, portraits, cards, bg_name, bg_color=WHITE, hud=None):
    super().__init__()
    ctx.store = store
    ctx.title = title
    ctx.subtitle = subtitle
    ctx.portraitgroup = PortraitGroup(portraits)
    ctx.cards = cards
    ctx.bg = None
    ctx.bg_name = bg_name
    ctx.bg_color = bg_color
    ctx.messages = messages
    ctx.focuses = 0
    ctx.blurring = False
    ctx.exiting = False
    ctx.bubble = None
    ctx.textbox = TextBox((96, 32), color=WHITE)
    ctx.hud = hud or Hud(store.party)
    ctx.hud._pos = (8, 8)
    ctx.anims = [CursorAnim()]
    ctx.on_animate = None
    ctx.controls = [
      Control(key=("X"), value="Menu")
    ]

  def enter(ctx):
    ctx.anims.append(HudEnterAnim(duration=20))
    ctx.get_head().transition([SlideDown(on_end=lambda: (
      ctx.anims.extend([
        BackgroundSlideupAnim(duration=15),
        BackgroundEnterAnim(duration=15, delay=10),
        *animate_text(anim=SubtitleEnterAnim, text=ctx.subtitle, period=3, stagger=1, delay=15),
        SubtitleSlideAnim(duration=15, delay=len(ctx.subtitle) + 10),
        *animate_text(anim=TitleEnterAnim, text=ctx.title, period=5, stagger=3, delay=45),
        BoxEnterAnim(duration=20, delay=90)
      ]),
      ctx.portraitgroup.enter(on_end=ctx.focus)
    ))])

  def exit(ctx):
    ctx.exiting = True
    ctx.bubble.exit()
    ctx.portraitgroup.exit()
    ctx.child.exit()
    ctx.anims += [
      BackgroundExitAnim(duration=15),
      PortraitExitAnim(duration=8, delay=15),
      BoxExitAnim(duration=8),
      TitleSlideoutAnim(duration=8),
    ]
    ctx.on_animate = lambda: ctx.close(None)

  def focus(ctx):
    portrait = ctx.portraitgroup.portraits[0]
    portrait.start_talk()
    message = (ctx.focuses == 0
      and ctx.messages["home"]
      or ctx.messages["home_again"])
    ctx.bubble = TextBubble(width=104, pos=(240, 40))
    ctx.bubble.print(message, on_end=lambda: (
      portrait.stop_talk(),
      ctx.child is None and ctx.open(
        CardContext(
          cards=map(lambda data: data.name, ctx.cards),
          pos=(56, 136),
          on_select=lambda card: (
            text := next((c.text for c in ctx.cards if c.name == card.name), None),
            text and ctx.textbox.print(text)
          ),
          on_choose=ctx.handle_choose
        )
      )
    ))
    if ctx.child:
      ctx.child.focus()
      ctx.textbox.clear()
      ctx.blurring = False
      ctx.anims += [
        TitleSlideinAnim(duration=12),
        BoxEnterAnim(duration=20)
      ]
    ctx.focuses += 1

  def blur(ctx):
    ctx.blurring = True
    ctx.anims += [
      TitleSlideoutAnim(duration=7),
      BoxExitAnim(duration=7)
    ]

  def handle_choose(ctx, card):
    if card.name == "exit": return ctx.handle_exit()
    if card.name == "buy": return ctx.handle_buy(card)
    ctx.portraitgroup.cycle()
    if card.name == "sell": return ctx.handle_sell(card)

  def handle_buy(ctx, card):
    ctx.blur()
    ctx.bubble.exit(on_end=lambda: setattr(ctx, "bubble", None))
    ctx.child.open(BuyContext(
      store=ctx.store,
      comps=ComponentStore(
        hud=ctx.hud,
        goldbubble=GoldBubble(gold=ctx.store.gold),
        textbubble=TextBubble(width=120, origin=Sprite.ORIGIN_TOP, offset=(32, 0)),
        bagbubble=None,
        portraitgroup=ctx.portraitgroup,
        card=card,
      )
    ), on_close=ctx.focus)

  def handle_sell(ctx, card):
    ctx.blur()
    ctx.child.open(SellContext(
      store=ctx.store,
      bubble=ctx.bubble,
      portrait=ctx.portraitgroup.portraits[0],
      messages=ctx.messages["sell"],
      hud=ctx.hud,
      card=card,
      on_close=lambda: (
        ctx.portraitgroup.stop_cycle(),
        ctx.focus()
      )
    ))

  def handle_exit(ctx):
    portrait = ctx.portraitgroup.portraits[0]
    portrait.start_talk()
    ctx.bubble.print(ctx.messages["exit"], on_end=lambda: (
      ctx.anims.append(Anim(duration=45, on_end=ctx.exit)),
      portrait.stop_talk()
    ))

  def update(ctx):
    super().update()
    ctx.portraitgroup.update()
    for anim in ctx.anims:
      if anim.done:
        ctx.anims.remove(anim)
        if (anim.blocking
        and not next((a for a in ctx.anims if a.blocking), None)
        and ctx.on_animate):
          ctx.on_animate()
      else:
        anim.update()

  def view(ctx):
    MARGIN = 2
    sprites = []
    is_home = not ctx.child or isinstance(ctx.get_tail(), CardContext)

    hud = ctx.hud
    hud_goal = (MARGIN, WINDOW_HEIGHT - MARGIN - hud.render().get_height())
    if is_home and hud.pos != hud_goal:
      hud.slide(hud.pos, hud_goal)
    hud_view = hud.view()
    if hud_view:
      sprites += Sprite.move_all(
        sprites=hud_view,
        offset=(0, hud.image.get_height() / 2),
        origin=Sprite.ORIGIN_LEFT,
        layer="hud",
      )

    if ctx.get_head().transits:
      return sprites

    bg_image = Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    bg_image.fill(BLACK)
    sprites.append(Sprite(
      image=bg_image,
      pos=(0, 0)
    ))

    if ctx.bg_name.endswith("bgtile"):
      if not ctx.bg:
        ctx.bg = Bg(sprite_id=ctx.bg_name)
        ctx.bg.enter()
      sprites += Sprite.move_all(
        sprites=ctx.bg.view(),
        offset=(0, -WINDOW_HEIGHT / 2 + BG_HEIGHT / 2)
      )
      if is_home:
        sprites += [Sprite(
          image=Surface((WINDOW_WIDTH, BOTTOMBAR_HEIGHT)),
          pos=(0, BG_HEIGHT)
        )]
    else:
      bg_image = assets.sprites[ctx.bg_name]
      bg_image = replace_color(bg_image, WHITE, ctx.bg_color)
      bg_anim = next((a for a in ctx.anims if isinstance(a, BackgroundAnim)), None)
      if bg_anim:
        t = bg_anim.pos
        if type(bg_anim) is BackgroundExitAnim:
          t = 1 - t
        if t < 0.5:
          t = t / 0.5
          bg_width = int(bg_image.get_width() * t)
          bg_height = 4
        else:
          t = (t - 0.5) / 0.5
          bg_width = bg_image.get_width()
          bg_height = int(bg_image.get_height() * t)
        bg_image = scale(bg_image, (bg_width, bg_height))
      if bg_anim or not ctx.exiting:
        sprites.append(Sprite(
          image=bg_image,
          pos=(
            WINDOW_WIDTH / 2 - bg_image.get_width() / 2,
            128 / 2 - bg_image.get_height() / 2
          )
        ))

    sprites += Sprite.move_all(
      sprites=ctx.portraitgroup.view(),
      layer="portrait",
    )

    if ctx.bubble:
      sprites += Sprite.move_all(
        sprites=ctx.bubble.view(),
        layer="textbox",
      )

    title_anim = next((a for a in ctx.anims if (
      isinstance(a, TitleAnim)
      or isinstance(a, SubtitleAnim)
    )), None)
    if (title_anim
    or not ctx.exiting
    and (not ctx.child or ctx.child.child is None)):
      title_text = ctx.title
      title_font = assets.ttf["english_large"]
      title_width, title_height = title_font.size(title_text)
      title_x = WINDOW_WIDTH - title_width - 8
      title_y = WINDOW_HEIGHT - title_height - 7
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
      if title_anim or not ctx.blurring:
        char_x = title_x
        char_y = title_y
        for i, char in enumerate(title_text):
          char_anim = next((a for a in ctx.anims if type(a) is TitleEnterAnim and a.target == i), None)
          if char_anim:
            t = char_anim.pos
            c = int(0xFF * t)
            char_offset = (1 - ease_out(t)) * 12
            char_color = Color(c, c, c)
          else:
            c = 255
            char_offset = 0
            char_color = WHITE
          if c:
            char_image = title_font.render(char, char_color)
            char_width = char_image.get_width()
            sprites.append(Sprite(
              image=char_image,
              pos=(char_x + char_offset, char_y + char_offset)
            ))
          else:
            char_width = title_font.width(char)
          char_x += char_width

      subtitle_text = ctx.subtitle
      subtitle_font = assets.ttf["normal"]
      subtitle_width, subtitle_height = subtitle_font.size(subtitle_text)
      subtitle_x = title_x + title_width - subtitle_width
      subtitle_y = title_y - title_height + 2
      subtitle_anim = next((a for a in ctx.anims if type(a) is SubtitleSlideAnim), None)
      if subtitle_anim:
        t = subtitle_anim.pos
        if type(subtitle_anim) is SubtitleSlideAnim:
          t = ease_out(t)
          subtitle_y = lerp(WINDOW_HEIGHT - subtitle_height - 7, subtitle_y, t)
      if subtitle_anim or title_anim or not ctx.blurring:
        char_x = subtitle_x
        char_y = subtitle_y
        for i, char in enumerate(subtitle_text):
          char_anim = next((a for a in ctx.anims if type(a) is SubtitleEnterAnim and a.target == i), None)
          if char_anim:
            t = char_anim.pos
            c = int(0xFF * t)
            char_offset = (1 - ease_out(t)) * 12
            char_color = Color(c, c, c)
          else:
            c = 255
            char_offset = 0
            char_color = WHITE
          if c:
            char_image = subtitle_font.render(char, char_color)
            char_width = char_image.get_width()
            sprites.append(Sprite(
              image=char_image,
              pos=(char_x + char_offset, char_y + char_offset)
            ))
          else:
            char_width = title_font.width(char)
          char_x += char_width

    box_image = Box(sprite_prefix="item_tile", size=(116, 48)).render()
    box_x = 168
    box_y = 112
    box_anim = next((a for a in ctx.anims if isinstance(a, BoxAnim)), None)
    if box_anim:
      t = box_anim.pos
      if type(box_anim) is BoxEnterAnim:
        t = ease_out(t)
      elif type(box_anim) is BoxExitAnim:
        t = 1 - t
      box_x = lerp(WINDOW_WIDTH, box_x, t)
    if box_anim or not ctx.blurring and not ctx.exiting:
      sprites.append(Sprite(
        image=box_image,
        pos=(box_x, box_y),
        layer="textbox",
      ))
      if not box_anim:
        sprites.append(Sprite(
          image=ctx.textbox.render(),
          pos=(box_x + 10, box_y + 8),
          layer="textbox",
        ))

    if ctx.child:
      sprites += super().view()

    LAYERS = ["bg", "item", "cursor", "pricetag", "topbar", "bottombar", "portrait", "textbox", "counter", "card", "hand", "hud"]
    sprites.sort(key=lambda s: (
      LAYERS.index(s.layer) + 1 if s.layer in LAYERS else 0
    ))

    return sprites
