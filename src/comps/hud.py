import math
import random
import pygame
from pygame import Surface, Rect, PixelArray

import palette
from assets import load as use_assets
from filters import replace_color, recolor, outline
from text import render_char, render as render_text

from actors.knight import Knight
from actors.mage import Mage

from anims import Anim
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
FLINCH_DURATION = 10
SWITCHOUT_DURATION = 6
SWITCHIN_DURATION = 12

class EnterAnim(TweenAnim):
  def __init__(anim):
    super().__init__(duration=ENTER_DURATION)

class ExitAnim(TweenAnim):
  def __init__(anim):
    super().__init__(duration=EXIT_DURATION)

class FlinchAnim(Anim):
  def __init__(anim):
    super().__init__(duration=FLINCH_DURATION)

class SwitchOutAnim(TweenAnim):
  def __init__(anim):
    super().__init__(duration=SWITCHOUT_DURATION)

class SwitchInAnim(TweenAnim):
  def __init__(anim):
    super().__init__(duration=SWITCHIN_DURATION)

class Hud:
  def __init__(panel):
    panel.sprite = None
    panel.active = True
    panel.anims = []
    panel.anims_drawn = 0
    panel.hero = None
    panel.hp_hero = math.inf
    panel.hp_ally = math.inf
    panel.offset = (0, 0)
    panel.enter()

  def enter(panel):
    panel.active = True
    panel.anims.append(EnterAnim())

  def exit(panel):
    panel.active = False
    panel.anims.append(ExitAnim())

  def update(panel, hero, ally):
    if (panel.sprite is None
    or panel.anims_drawn
    or hero != panel.hero
    or hero.hp != panel.hp_hero
    or ally.hp != panel.hp_ally):
      if hero != panel.hero:
        panel.anims.append(SwitchOutAnim())
        panel.anims.append(SwitchInAnim())
        panel.hero = hero
        panel.hp_hero = hero.hp
        panel.hp_ally = ally.hp
      elif hero.hp < panel.hp_hero or ally.hp < panel.hp_ally:
        panel.anims.append(FlinchAnim())
        panel.hp_hero = hero.hp
        panel.hp_ally = ally.hp
      anim = panel.anims[0] if panel.anims else None
      panel.anims_drawn = len(panel.anims)
      panel.sprite = panel.render(hero, ally, anim)

  def render(panel, hero, ally, anim=None):
    assets = use_assets()
    width = assets.sprites["hud"].get_width() + 1
    height = assets.sprites["hud"].get_height()
    sprite = Surface((width, height))
    sprite.fill(0xFF00FF)
    sprite.set_colorkey(0xFF00FF)
    sprite.blit(assets.sprites["hud"], (0, 0))

    if (type(hero) is Knight and type(anim) is not SwitchOutAnim
    or type(hero) is Mage and type(anim) is SwitchOutAnim):
      hero_portrait = assets.sprites["circle_knight"]
      ally_portrait = assets.sprites["circ16_mage"]
    if (type(hero) is Mage and type(anim) is not SwitchOutAnim
    or type(hero) is Knight and type(anim) is SwitchOutAnim):
      hero_portrait = assets.sprites["circle_mage"]
      ally_portrait = assets.sprites["circ16_knight"]

    if hero.dead:
      hero_portrait = replace_color(hero_portrait, palette.WHITE, palette.BLACK)
      hero_portrait = replace_color(hero_portrait, palette.BLUE, palette.RED)
    if ally.dead:
      ally_portrait = replace_color(ally_portrait, palette.WHITE, palette.BLACK)
      ally_portrait = replace_color(ally_portrait, palette.BLUE, palette.RED)

    hero_scaled = hero_portrait
    ally_scaled = ally_portrait
    if type(anim) in (SwitchOutAnim, SwitchInAnim):
      t = anim.pos
      if type(anim) is SwitchInAnim:
        t = 1 - ease_out(t)
      ally_width = lerp(ally_portrait.get_width(), 0, t)
      ally_height = lerp(ally_portrait.get_height(), 0, t)
      hero_width = lerp(hero_portrait.get_width(), 0, t)
      hero_height = hero_portrait.get_height()
      ally_scaled = pygame.transform.scale(ally_portrait, (int(ally_width), int(ally_height)))
      hero_scaled = pygame.transform.scale(hero_portrait, (int(hero_width), int(hero_height)))

    sprite.blit(hero_scaled, (
      hero_portrait.get_width() // 2 - hero_scaled.get_width() // 2,
      hero_portrait.get_height() // 2 - hero_scaled.get_height() // 2
    ))
    sprite.blit(ally_scaled, (
      CIRC16_X + ally_portrait.get_width() // 2 - ally_scaled.get_width() // 2,
      CIRC16_Y + ally_portrait.get_height() // 2 - ally_scaled.get_height() // 2
    ))
    sprite.blit(assets.sprites["hp"], (HP_X, HP_Y))

    hp_text = str(math.ceil(max(0, hero.hp)))
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

    number = render_text(str(hero.hp_max), assets.fonts["smallcaps"])
    number = outline(number, palette.BLACK)
    number = outline(number, palette.WHITE)
    sprite.blit(number, (HP_MAX_X, HP_MAX_Y))

    draw_bar(sprite, hero.hp / hero.hp_max, HP_BAR_X, HP_BAR_Y1)
    draw_bar(sprite, ally.hp / ally.hp_max, HP_BAR_X, HP_BAR_Y2)
    return sprite

  def draw(panel, surface, ctx):
    panel.update(ctx.hero, ctx.ally)
    sprite = panel.sprite
    hidden_x, hidden_y = MARGIN_LEFT, -sprite.get_height()
    corner_x, corner_y = MARGIN_LEFT, MARGIN_TOP
    anim = panel.anims[0] if panel.anims else None
    if anim:
      t = anim.update()
      if type(anim) is EnterAnim:
        t = ease_out(t)
        start_x, start_y = hidden_x, hidden_y
        target_x, target_y = corner_x, corner_y
      elif type(anim) is ExitAnim:
        start_x, start_y = corner_x, corner_y
        target_x, target_y = hidden_x, hidden_y
      elif type(anim) is FlinchAnim:
        offset_x, offset_y = panel.offset
        while (offset_x, offset_y) == panel.offset:
          offset_x = random.randint(-1, 1)
          offset_y = random.randint(-1, 1)
        x = corner_x + offset_x
        y = corner_y + offset_y
      else:
        x = corner_x
        y = corner_y

      if type(anim) is EnterAnim or type(anim) is ExitAnim:
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

def draw_bar(surface, pct, x, y):
  pygame.draw.rect(surface, palette.WHITE, Rect(
    (x, y),
    (HP_HALFWIDTH * min(0.5, pct) / 0.5, 1)
  ))
  if pct > 0.5:
    pygame.draw.rect(surface, palette.WHITE, Rect(
      (x + HP_HALFWIDTH - 1, y + 1),
      (HP_HALFWIDTH * min(1, (pct - 0.5) / 0.5), 1)
    ))
