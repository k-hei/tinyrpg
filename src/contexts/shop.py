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

class ShopContext(Context):
  def __init__(ctx, items):
    super().__init__()
    ctx.items = items
    ctx.hero = KnightCore()
    ctx.portraits = [MiraPortrait()]
    ctx.hud = Hud()
    ctx.anims = [CursorAnim()]
    ctx.bubble = TextBubble(width=96, pos=(128, 40))
    ctx.controls = [
      Control(key=("X"), value="Menu")
    ]
    ctx.open(CardContext(pos=(16, 144), on_choose=ctx.handle_choose))

  def enter(ctx):
    ctx.anims += [
      BackgroundEnterAnim(duration=15),
      PortraitEnterAnim(
        duration=20,
        delay=10,
        on_end=ctx.focus
      )
    ]

  def focus(ctx):
    portrait = ctx.portraits[0]
    portrait.start_talk(),
    ctx.bubble.print("MIRA: What can I do you for?", on_end=portrait.stop_talk)
    ctx.child.focus()

  def handle_choose(ctx, card):
    if card.name == "buy": return
    if card.name == "sell": ctx.handle_sell(card)
    if card.name == "exit": return

  def handle_sell(ctx, card):
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

    if ctx.child.child is None:
      title_image = assets.ttf["english_large"].render("Fortune House")
      title_x = surface.get_width() - title_image.get_width() - 8
      title_y = surface.get_height() - title_image.get_height() - 7
      surface.blit(title_image, (title_x, title_y))

      subtitle_image = assets.ttf["roman"].render("Destiny written in starlight")
      subtitle_x = title_x + title_image.get_width() - subtitle_image.get_width()
      subtitle_y = title_y - title_image.get_height() + 2
      surface.blit(subtitle_image, (subtitle_x, subtitle_y))

    if type(ctx.child) is CardContext:
      sprites = ctx.child.view()
      for sprite in sprites:
        sprite.draw(surface)
    elif ctx.child:
      ctx.child.draw(surface)
