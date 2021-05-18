import math
import random
import pygame
from pygame import Surface, Rect, PixelArray

from palette import BLACK, WHITE, BLUE, RED, CYAN, GRAY
from assets import load as use_assets
from filters import replace_color, recolor, outline
from text import render_char, render as render_text, find_width as find_text_width

from cores.knight import KnightCore
from cores.mage import MageCore

from anims import Anim
from anims.tween import TweenAnim
from easing.expo import ease_out, ease_in
from lib.lerp import lerp

CIRC16_X = 28
CIRC16_Y = 26
HP_X = 31
HP_Y = 0
HP_VALUE_X = 48
HP_VALUE_Y = 0
HP_MAX_X = 18
HP_MAX_Y = 7
HP_BAR_X = 52
HP_BAR_Y1 = 18
HP_BAR_Y2 = 28
HP_HALFWIDTH = 13
HP_CRITICAL = 5
SPEED_DEPLETE = 200
SPEED_RESTORE = 100
ENTER_DURATION = 15
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
  MARGIN_LEFT = 8
  MARGIN_TOP = 8

  def __init__(panel, parent):
    panel.parent = parent
    panel.sprite = None
    panel.active = True
    panel.anims = []
    panel.anims_drawn = 0
    panel.hero = None
    panel.ally = None
    panel.hp_hero = math.inf
    panel.hp_ally = math.inf
    panel.hp_hero_drawn = math.inf
    panel.hp_ally_drawn = math.inf
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
    or ally != panel.ally
    or hero.get_hp() != panel.hp_hero
    or ally and ally.get_hp() != panel.hp_ally):
      if hero != panel.hero:
        if panel.hero is not None:
          panel.anims.append(SwitchOutAnim())
          panel.anims.append(SwitchInAnim())
        panel.hero = hero
        panel.hp_hero = hero.get_hp()
      if ally != panel.ally:
        panel.ally = ally
        panel.hp_ally = ally.get_hp()
      elif (hero.get_hp() < panel.hp_hero_drawn
      or ally and ally.get_hp() < panel.hp_ally_drawn):
        flinching = False
        if panel.hp_hero == math.inf:
          panel.hp_hero = hero.get_hp_max()
        else:
          flinching = True
        if ally and panel.hp_ally == math.inf:
          panel.hp_ally = ally.get_hp_max()
        else:
          flinching = False
        if flinching:
          panel.anims.append(FlinchAnim())
      anim = panel.anims[0] if panel.anims else None
      panel.anims_drawn = len(panel.anims)
      if anim is None and panel.hp_hero > hero.get_hp():
        panel.hp_hero = max(hero.get_hp(), panel.hp_hero - hero.get_hp_max() / SPEED_DEPLETE)
      if anim is None and panel.hp_hero < hero.get_hp():
        panel.hp_hero = min(hero.get_hp(), panel.hp_hero + hero.get_hp_max() / SPEED_RESTORE)
      if anim is None and ally and panel.hp_ally > ally.get_hp():
        panel.hp_ally = max(ally.get_hp(), panel.hp_ally - ally.get_hp_max() / SPEED_DEPLETE)
      if anim is None and ally and panel.hp_ally < ally.get_hp():
        panel.hp_ally = min(ally.get_hp(), panel.hp_ally + ally.get_hp_max() / SPEED_RESTORE)
      panel.sprite = panel.render(hero, ally, anim)
    panel.hp_hero_drawn = hero.get_hp()
    if ally:
      panel.hp_ally_drawn = ally.get_hp()

  def render(panel, hero, ally, anim=None):
    assets = use_assets()
    width = assets.sprites["hud"].get_width() + 1
    height = assets.sprites["hud"].get_height()
    sprite = Surface((width, height)).convert_alpha()
    sprite.blit(assets.sprites["hud"], (0, 0))

    hero_portrait = None
    if (type(hero) is KnightCore and type(anim) is not SwitchOutAnim
    or type(hero) is MageCore and type(anim) is SwitchOutAnim):
      hero_portrait = assets.sprites["circle_knight"]
    if (type(hero) is MageCore and type(anim) is not SwitchOutAnim
    or type(hero) is KnightCore and type(anim) is SwitchOutAnim):
      hero_portrait = assets.sprites["circle_mage"]

    ally_portrait = None
    if (type(ally) is KnightCore and type(anim) is not SwitchOutAnim
    or type(ally) is MageCore and type(anim) is SwitchOutAnim):
      ally_portrait = assets.sprites["circ16_knight"]
    if (type(ally) is MageCore and type(anim) is not SwitchOutAnim
    or type(ally) is KnightCore and type(anim) is SwitchOutAnim):
      ally_portrait = assets.sprites["circ16_mage"]

    if hero.dead:
      hero_portrait = replace_color(hero_portrait, WHITE, BLACK)
      hero_portrait = replace_color(hero_portrait, BLUE, RED)
    if ally and ally.dead:
      ally_portrait = replace_color(ally_portrait, WHITE, BLACK)
      ally_portrait = replace_color(ally_portrait, BLUE, RED)

    hero_scaled = hero_portrait
    ally_scaled = ally_portrait
    if type(anim) in (SwitchOutAnim, SwitchInAnim):
      t = anim.pos
      if type(anim) is SwitchInAnim:
        t = 1 - ease_out(t)
      hero_width = lerp(hero_portrait.get_width(), 0, t)
      hero_height = hero_portrait.get_height()
      hero_scaled = pygame.transform.scale(hero_portrait, (int(hero_width), int(hero_height)))
      if ally:
        ally_width = lerp(ally_portrait.get_width(), 0, t)
        ally_height = lerp(ally_portrait.get_height(), 0, t)
        ally_scaled = pygame.transform.scale(ally_portrait, (int(ally_width), int(ally_height)))

    sprite.blit(hero_scaled, (
      hero_portrait.get_width() // 2 - hero_scaled.get_width() // 2,
      hero_portrait.get_height() // 2 - hero_scaled.get_height() // 2
    ))
    if ally:
      sprite.blit(ally_scaled, (
        CIRC16_X + ally_portrait.get_width() // 2 - ally_scaled.get_width() // 2,
        CIRC16_Y + ally_portrait.get_height() // 2 - ally_scaled.get_height() // 2
      ))
    sprite.blit(assets.sprites["hp"], (HP_X, HP_Y))

    hp_text = render_numbers(hero.get_hp(), hero.get_hp_max(), HP_CRITICAL)
    sprite.blit(hp_text, (HP_VALUE_X, HP_VALUE_Y))

    if hero.get_hp() <= panel.hp_hero:
      draw_bar(sprite, panel.hp_hero / hero.get_hp_max(), (HP_BAR_X, HP_BAR_Y1), RED)
      draw_bar(sprite, hero.get_hp() / hero.get_hp_max(), (HP_BAR_X, HP_BAR_Y1))
    else:
      draw_bar(sprite, hero.get_hp() / hero.get_hp_max(), (HP_BAR_X, HP_BAR_Y1), CYAN)
      draw_bar(sprite, panel.hp_hero / hero.get_hp_max(), (HP_BAR_X, HP_BAR_Y1))

    if ally:
      if ally.get_hp() <= panel.hp_ally:
        draw_bar(sprite, panel.hp_ally / ally.get_hp_max(), (HP_BAR_X, HP_BAR_Y2), RED)
        draw_bar(sprite, ally.get_hp() / ally.get_hp_max(), (HP_BAR_X, HP_BAR_Y2))
      else:
        draw_bar(sprite, ally.get_hp() / ally.get_hp_max(), (HP_BAR_X, HP_BAR_Y2), CYAN)
        draw_bar(sprite, panel.hp_ally / ally.get_hp_max(), (HP_BAR_X, HP_BAR_Y2))


    return sprite

  def draw(panel, surface):
    ctx = panel.parent
    panel.update(ctx.hero.core, ctx.ally and ctx.ally.core)
    sprite = panel.sprite
    hidden_x, hidden_y = Hud.MARGIN_LEFT, -sprite.get_height()
    corner_x, corner_y = Hud.MARGIN_LEFT, Hud.MARGIN_TOP
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

def draw_bar(surface, pct, pos, color=WHITE):
  x, y = pos
  pygame.draw.rect(surface, color, Rect(
    (x, y),
    (HP_HALFWIDTH * min(0.5, pct) / 0.5, 1)
  ))
  if pct > 0.5:
    pygame.draw.rect(surface, color, Rect(
      (x + HP_HALFWIDTH - 1, y + 1),
      (HP_HALFWIDTH * min(1, (pct - 0.5) / 0.5), 1)
    ))

def render_numbers(hp, hp_max, crit_threshold=0):
  assets = use_assets()

  hp_text = str(math.ceil(max(0, hp)))
  if len(hp_text) == 1:
    hp_text = "0" + hp_text
    gray = True
  else:
    gray = False

  hp_max = str(hp_max)
  if len(hp_max) == 1:
    hp_max = "0" + hp_max

  sprite_slash = assets.sprites["hud_slash"]
  sprite_firstno = render_char(hp_text[0], assets.fonts["numbers16"])
  sprite_hpmax = render_text(hp_max, assets.fonts["smallcaps"])
  sprite_width = sprite_firstno.get_width() - 1
  sprite_width += find_text_width(hp_text[1:], assets.fonts["numbers13"])
  sprite_width += sprite_slash.get_width()
  sprite_width += sprite_hpmax.get_width()
  sprite_height = sprite_firstno.get_height()

  sprite = Surface((sprite_width, sprite_height)).convert_alpha()

  if gray:
    pixels = PixelArray(sprite_firstno)
    pixels.replace(WHITE, GRAY)
    pixels.close()
  sprite.blit(sprite_firstno, (0, 0))

  x = sprite_firstno.get_width() - 1

  for char in hp_text[1:]:
    number = render_char(char, assets.fonts["numbers13"]).convert_alpha()
    if hp <= crit_threshold:
      pixels = PixelArray(number)
      pixels.replace(BLACK, RED)
      pixels.close()
    sprite.blit(number, (x, HP_VALUE_Y))
    x += number.get_width() - 2

  sprite.blit(sprite_slash, (x, HP_MAX_Y))

  sprite_hpmax = outline(sprite_hpmax, BLACK)
  sprite_hpmax = outline(sprite_hpmax, WHITE)
  sprite.blit(sprite_hpmax, (HP_MAX_X, HP_MAX_Y))
  return sprite
