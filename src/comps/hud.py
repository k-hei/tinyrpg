import math
import pygame
from pygame import Surface, Rect, PixelArray

import palette
from assets import load as use_assets
from filters import replace_color, recolor, outline
from text import render_char, render as render_text

from actors.knight import Knight
from actors.mage import Mage

from anims.tween import TweenAnim
from easing.expo import ease_out, ease_in
from lerp import lerp

MARGIN_LEFT = 8
MARGIN_TOP = 8
CIRC16_X = 28
CIRC16_Y = 26
HP_X = 31
HP_Y = 0
HP_VALUE_X = 48
HP_VALUE_Y = 0
HP_MAX_X = 66
HP_MAX_Y = 7
HP_BAR_X = 52
HP_BAR_Y1 = 18
HP_BAR_Y2 = 28
HP_HALFWIDTH = 13
ENTER_DURATION = 8
EXIT_DURATION = 6

class Hud:
  def __init__(panel):
    panel.surface = None
    panel.active = True
    panel.anims = []
    panel.enter()

  def enter(panel):
    panel.active = True
    panel.anims.append(TweenAnim(duration=ENTER_DURATION))

  def exit(panel):
    panel.active = False
    panel.anims.append(TweenAnim(duration=EXIT_DURATION))

  def render(panel, ctx):
    assets = use_assets()
    width = assets.sprites["hud"].get_width() + 1
    height = assets.sprites["hud"].get_height()
    sprite = Surface((width, height))
    sprite.fill(0xFF00FF)
    sprite.set_colorkey(0xFF00FF)
    sprite.blit(assets.sprites["hud"], (0, 0))

    if type(ctx.hero) is Knight:
      hero_portrait = assets.sprites["circle_knight"]
      ally_portrait = assets.sprites["circ16_mage"]
    elif type(ctx.hero) is Mage:
      hero_portrait = assets.sprites["circle_mage"]
      ally_portrait = assets.sprites["circ16_knight"]

    if ctx.hero.dead:
      hero_portrait = replace_color(hero_portrait, palette.WHITE, palette.BLACK)
      hero_portrait = replace_color(hero_portrait, palette.BLUE, palette.RED)
    if ctx.ally.dead:
      ally_portrait = replace_color(ally_portrait, palette.WHITE, palette.BLACK)
      ally_portrait = replace_color(ally_portrait, palette.BLUE, palette.RED)

    sprite.blit(hero_portrait, (0, 0))
    sprite.blit(ally_portrait, (CIRC16_X, CIRC16_Y))

    sprite.blit(assets.sprites["hp"], (HP_X, HP_Y))

    hp_text = str(math.ceil(max(0, ctx.hero.hp)))
    gray = False
    if len(hp_text) == 1:
      hp_text = "0" + hp_text
      gray = True

    first_number = render_char(hp_text[0], assets.fonts["numbers16"])
    if gray:
      pixels = PixelArray(first_number)
      pixels.replace(palette.WHITE, palette.GRAY)
      pixels.close()
    sprite.blit(first_number, (HP_VALUE_X, HP_VALUE_Y))

    x = HP_VALUE_X + first_number.get_width() - 1
    for char in hp_text[1:]:
      number = render_text(char, assets.fonts["numbers13"])
      sprite.blit(number, (x, HP_VALUE_Y))
      x += number.get_width() - 2

    number = render_text(str(ctx.hero.hp_max), assets.fonts["smallcaps"])
    number = outline(number, palette.BLACK)
    number = outline(number, palette.WHITE)
    sprite.blit(number, (HP_MAX_X, HP_MAX_Y))

    halfmax1 = ctx.hero.hp_max // 2
    bar1_half1 = min(halfmax1, ctx.hero.hp) / halfmax1
    pygame.draw.rect(sprite, palette.WHITE, Rect(
      HP_BAR_X,
      HP_BAR_Y1,
      HP_HALFWIDTH * bar1_half1,
      1
    ))
    if ctx.hero.hp > halfmax1:
      bar1_half2 = min(1, (ctx.hero.hp - halfmax1) / halfmax1)
      pygame.draw.rect(sprite, palette.WHITE, Rect(
        HP_BAR_X + HP_HALFWIDTH - 1,
        HP_BAR_Y1 + 1,
        HP_HALFWIDTH * bar1_half2,
        1
      ))

    halfmax2 = ctx.ally.hp_max // 2
    bar2_half1 = min(halfmax2, ctx.ally.hp) / halfmax2
    pygame.draw.rect(sprite, palette.WHITE, Rect(
      HP_BAR_X,
      HP_BAR_Y2,
      HP_HALFWIDTH * bar2_half1,
      1
    ))
    if ctx.ally.hp > halfmax2:
      bar2_half2 = min(1, (ctx.ally.hp - halfmax2) / halfmax2)
      pygame.draw.rect(sprite, palette.WHITE, Rect(
        HP_BAR_X + HP_HALFWIDTH - 1,
        HP_BAR_Y2 + 1,
        HP_HALFWIDTH * bar2_half2,
        1
      ))

    return sprite

  def draw(panel, surface, ctx):
    assets = use_assets()
    sprite = panel.render(ctx)

    hidden_x, hidden_y = MARGIN_LEFT, -sprite.get_height()
    corner_x, corner_y = MARGIN_LEFT, MARGIN_TOP

    anim = panel.anims[0] if panel.anims else None
    if anim:
      t = anim.update()
      if panel.active:
        t = ease_out(t)
        start_x, start_y = hidden_x, hidden_y
        target_x, target_y = corner_x, corner_y
      else:
        start_x, start_y = corner_x, corner_y
        target_x, target_y = hidden_x, hidden_y
      x = lerp(start_x, target_x, t)
      y = lerp(start_y, target_y, t)
      if anim.done:
        panel.anims.pop(0)
    elif panel.active:
      x = corner_x
      y = corner_y
    else:
      return

    surface.blit(sprite, (x, y))
