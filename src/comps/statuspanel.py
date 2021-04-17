import math
import pygame
from pygame import Surface, Rect

from assets import load as use_assets
import palette

from lerp import lerp
from easing.expo import ease_out, ease_in
from filters import replace_color, recolor
from text import render as render_text

from actors.knight import Knight
from actors.mage import Mage
from anims.tween import TweenAnim

ENTER_DURATION = 20
ENTER_STAGGER = 5
EXIT_DURATION = 6
EXIT_STAGGER = 3
PANEL_SPACING = -3
MARGIN_X = 8
MARGIN_Y = 6
STATUS_PADDING_X = 10
STATUS_PADDING_Y = 4
STATUS_FIELD_SPACING = 1
BAR_X = 2
BAR_Y = 7
BAR_PADDING_X = 3
BAR_PADDING_Y = 1
BAR_WIDTH = 42
BAR_HEIGHT = 2
FLOOR_PADDING_LEFT = 3
FLOOR_PADDING_TOP = 3

class StatusPanel:
  def __init__(panel):
    panel.surface = None
    panel.active = True
    panel.enter()

  def enter(panel):
    panel.active = True
    panel.anims = [
      TweenAnim(
        duration=ENTER_DURATION,
        delay=ENTER_STAGGER * 2,
        target=Knight
      ),
      TweenAnim(
        duration=ENTER_DURATION,
        delay=ENTER_STAGGER,
        target=Mage
      ),
      TweenAnim(
        duration=ENTER_DURATION,
        target="status"
      )
    ]

  def exit(panel):
    panel.active = False
    panel.anims = [
      TweenAnim(
        duration=EXIT_DURATION,
        delay=EXIT_STAGGER * 2,
        target=Knight
      ),
      TweenAnim(
        duration=EXIT_DURATION,
        delay=EXIT_STAGGER,
        target=Mage
      ),
      TweenAnim(
        duration=EXIT_DURATION,
        target="status"
      )
    ]

  def draw(panel, surface, ctx):
    assets = use_assets()
    portrait_knight = assets.sprites["portrait_knight"]
    portrait_mage = assets.sprites["portrait_mage"]

    hero = ctx.hero
    ally = ctx.ally
    knight = hero if type(hero) is Knight else ally
    mage = hero if type(hero) is Mage else ally

    if knight.dead and not knight in ctx.floor.actors:
      portrait_knight = replace_color(portrait_knight, palette.WHITE, palette.RED)
    elif type(hero) is not Knight:
      portrait_knight = replace_color(portrait_knight, palette.WHITE, palette.GRAY)

    if mage.dead and not mage in ctx.floor.actors:
      portrait_mage = replace_color(portrait_mage, palette.WHITE, palette.RED)
    elif type(hero) is not Mage:
      portrait_mage = replace_color(portrait_mage, palette.WHITE, palette.GRAY)

    start_y = -portrait_knight.get_height()
    end_y = MARGIN_Y
    easing = ease_out
    if not panel.active:
      start_y, end_y = (end_y, start_y)
      easing = lambda x: x # ease_in

    knight_y, mage_y, status_y = (end_y, end_y, end_y)
    for anim in panel.anims:
      x = anim.update()
      t = easing(x)
      y = lerp(start_y, end_y, t)
      if anim.target is Knight:
        knight_y = y
      elif anim.target is Mage:
        mage_y = y
      elif anim.target == "status":
        status_y = y
      if anim.done:
        panel.anims.remove(anim)

    knight_x = MARGIN_X
    mage_x = knight_x + portrait_knight.get_width() + PANEL_SPACING
    status_x = mage_x + portrait_mage.get_width() + PANEL_SPACING
    surface.blit(portrait_knight, (knight_x, knight_y))
    surface.blit(portrait_mage, (mage_x, mage_y))
    surface.blit(panel.render_status(
      hp=max(0, hero.get_hp()),
      hp_max=hero.get_hp_max(),
      sp=ctx.sp,
      sp_max=ctx.sp_max,
      floor=ctx.floors.index(ctx.floor) + 1
    ), (status_x, status_y))

  def render_status(panel, hp, hp_max, sp, sp_max, floor):
    assets = use_assets()
    bg = assets.sprites["hud"]
    hp_tag = assets.sprites["tag_hp"]
    sp_tag = assets.sprites["tag_sp"]
    bar = assets.sprites["bar"]
    stairs = assets.sprites["icon_stairs"]
    font = assets.fonts["smallcaps"]

    width = STATUS_PADDING_X
    width += hp_tag.get_width() + BAR_X
    width += BAR_WIDTH + BAR_PADDING_X * 2
    height = bg.get_height()
    surface = Surface((width, height))
    surface.set_colorkey((0xFF, 0x00, 0xFF))
    surface.fill((0xFF, 0x00, 0xFF))
    surface.blit(bg, (0, 0))

    # hp tag
    x = STATUS_PADDING_X
    y = STATUS_PADDING_Y
    surface.blit(hp_tag, (x, y))

    # hp bar
    x += hp_tag.get_width() + BAR_X
    y += BAR_Y
    surface.blit(panel.render_bar(hp, hp_max), (x, y))

    # hp text
    x = STATUS_PADDING_X + hp_tag.get_width() + BAR_X
    y = STATUS_PADDING_Y + 1
    hp = 1 if hp > 0 and hp < 1 else math.floor(hp)
    surface.blit(panel.render_values(hp, hp_max), (x, y))

    # sp tag
    x = STATUS_PADDING_X
    y = STATUS_PADDING_Y + hp_tag.get_height() + STATUS_FIELD_SPACING
    surface.blit(sp_tag, (x, y))

    # sp bar
    x += sp_tag.get_width() + BAR_X
    y += BAR_Y
    surface.blit(panel.render_bar(sp, sp_max), (x, y))

    # sp text
    x = STATUS_PADDING_X + sp_tag.get_width() + BAR_X
    y = STATUS_PADDING_Y + hp_tag.get_height() + STATUS_FIELD_SPACING + 1
    sp = 1 if sp > 0 and sp < 1 else math.floor(sp)
    surface.blit(panel.render_values(sp, sp_max), (x, y))

    # floor icon
    x = STATUS_PADDING_X
    y = STATUS_PADDING_Y
    y += hp_tag.get_height() + STATUS_FIELD_SPACING
    y += sp_tag.get_height() + STATUS_FIELD_SPACING
    surface.blit(stairs, (x, y))

    # floor text
    x += stairs.get_width() + FLOOR_PADDING_LEFT
    y += FLOOR_PADDING_TOP
    text = render_text(str(floor) + "F", font)
    text = recolor(text, palette.WHITE)
    surface.blit(text, (x, y))

    return surface

  def render_bar(panel, val_cur, val_max):
    assets = use_assets()
    font = assets.fonts["smallcaps"]
    surface = assets.sprites["bar_small"].copy()
    width = math.ceil(BAR_WIDTH * val_cur / val_max)
    if width == BAR_WIDTH and val_cur != val_max:
      width -= 1
    pygame.draw.rect(surface, palette.WHITE, Rect(
      BAR_PADDING_X,
      BAR_PADDING_Y,
      width,
      BAR_HEIGHT
    ))
    return surface

  def render_values(panel, val_cur, val_max):
    assets = use_assets()
    font = assets.fonts["smallcaps"]
    bg_hp = str(val_cur) if val_cur >= 10 else "0" + str(val_cur)
    fg_hp = str(val_cur) if val_cur >= 10 else "  " + str(val_cur)
    bg_hp_max = str(val_max) if val_max >= 10 else "0" + str(val_max)
    fg_hp_max = str(val_max) if val_max >= 10 else "  " + str(val_max)
    bg_text = render_text(bg_hp + "/" + bg_hp_max, font)
    bg_text = recolor(bg_text, palette.GRAY)
    fg_text = render_text(fg_hp + "/" + fg_hp_max, font)
    if val_cur > 0:
      fg_text = recolor(fg_text, palette.WHITE)
    else:
      fg_text = recolor(fg_text, palette.RED)
    bg_text.blit(fg_text, (0, 0))
    return bg_text
