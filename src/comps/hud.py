from math import ceil, inf
from random import randint
import pygame
from pygame import Rect, Surface, SRCALPHA
from pygame.transform import scale

from colors.palette import BLACK, WHITE, LIME, DARKGREEN, YELLOW, DARKYELLOW, BLUE, RED, DARKRED, CYAN, DARKCYAN, GRAY
from assets import load as use_assets
from lib.filters import replace_color, recolor, outline
from lib.sprite import Sprite
from text import render_char, render as render_text, find_width as find_text_width

from cores.knight import Knight
from cores.mage import Mage
from cores.rogue import Rogue

from anims import Anim
from anims.tween import TweenAnim
from anims.pause import PauseAnim
from easing.expo import ease_out, ease_in, ease_in_out
from lib.lerp import lerp
import lib.vector as vector

CIRC16_X = 29
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
HP_WIDTH = 26
HP_CRITICAL = 5
SPEED_DEPLETE = 200
SPEED_RESTORE = 300
MARGIN = 8

class EnterAnim(TweenAnim):
  duration = 15
  blocking = True

class ExitAnim(TweenAnim):
  duration = 6
  blocking = True

class SwitchOutAnim(TweenAnim):
  duration = 6
  blocking = True

class SwitchInAnim(TweenAnim):
  duration = 12
  blocking = True

class FlinchAnim(Anim):
  duration = 10
  blocking = True

class SlideAnim(TweenAnim):
  duration = 12
  blocking = False

class Hud:
  MARGIN_LEFT = 8
  MARGIN_TOP = 8

  def __init__(hud, party, hp=False, portrait=True):
    hud.party = party
    hud.draws_hp = hp
    hud.draws_portrait = portrait
    hud.image = None
    hud.active = False
    hud.anims = []
    hud.offset = (0, 0)
    hud.pos = (0, 0)
    hud.hero = None
    hud.ally = None
    hud.hp_hero = inf
    hud.hp_ally = inf
    hud.hp_hero_drawn = inf
    hud.hp_ally_drawn = inf
    hud.updated = False
    hud.time = 0

  @property
  def pos(hud):
    return hud._pos

  @pos.setter
  def pos(hud, pos):
    if "_pos" in dir(hud):
      hud.anims = [SlideAnim(target=(hud._pos, pos))]
    hud._pos = pos

  def enter(hud, on_end=None):
    hud.active = True
    hud_image = hud.image or hud.render()
    hud._pos = (MARGIN, -hud_image.get_height())
    hud.pos = (MARGIN, MARGIN)
    if hud.anims and on_end:
      hud.anims[-1].on_end = on_end

  def exit(hud, on_end=None):
    hud.active = False
    hud_image = hud.image or hud.render()
    hud._pos = (MARGIN, MARGIN)
    hud.pos = (MARGIN, -hud_image.get_height())
    if hud.anims and on_end:
      hud.anims[-1].on_end = on_end

  def slide(hud, start, goal):
    hud._pos = start
    hud.pos = goal

  def shake(hud):
    hud.anims.append(FlinchAnim())

  def update(hud, force=False):
    # if hud.updated and not force: return
    # hud.updated = True
    hero = hud.party[0] if len(hud.party) >= 1 else None
    ally = hud.party[1] if len(hud.party) >= 2 else None
    if (hud.image is None
    or hud.anims
    or hero != hud.hero
    or ally != hud.ally
    or hero.get_hp() != hud.hp_hero
    or ally and ally.get_hp() != hud.hp_ally):
      if hero != hud.hero:
        if hud.hero is not None:
          if hud.anims and type(hud.anims[0]) is PauseAnim: # TODO: insert before first pause anim
            hud.anims.insert(0, SwitchInAnim())
            hud.anims.insert(0, SwitchOutAnim())
          else:
            hud.anims.append(SwitchOutAnim())
            hud.anims.append(SwitchInAnim())
        hud.hero = hero
        hud.hp_hero = hero.get_hp()
      elif hero.get_hp() < hud.hp_hero_drawn:
        hud.shake()
        if hud.hp_hero == inf:
          hud.hp_hero = hero.get_hp_max()

      if ally != hud.ally:
        hud.ally = ally
        if ally:
          hud.hp_ally = ally.get_hp()
      elif ally and ally.get_hp() < hud.hp_ally_drawn:
        hud.shake()
        if hud.hp_ally == inf:
          hud.hp_ally = ally.get_hp_max()

      anim = next((a for a in hud.anims if a.blocking), None)

      if anim is None and hud.hp_hero > hero.get_hp():
        hud.hp_hero = max(hero.get_hp(), hud.hp_hero - hero.get_hp_max() / SPEED_DEPLETE)

      if anim is None and hud.hp_hero < hero.get_hp():
        hud.hp_hero = min(hero.get_hp(), hud.hp_hero + hero.get_hp_max() / SPEED_RESTORE)

      if anim is None and ally and hud.hp_ally > ally.get_hp():
        hud.hp_ally = max(ally.get_hp(), hud.hp_ally - ally.get_hp_max() / SPEED_DEPLETE)

      if anim is None and ally and hud.hp_ally < ally.get_hp():
        hud.hp_ally = min(ally.get_hp(), hud.hp_ally + ally.get_hp_max() / SPEED_RESTORE)

      anim = hud.anims[0] if hud.anims else None
      if anim:
        if anim.done:
          hud.anims.pop(0)
        else:
          anim.update()

    hud.hp_hero_drawn = hero.get_hp()
    if ally:
      hud.hp_ally_drawn = ally.get_hp()
    hud.time += 1

  def render(hud, portrait=True):
    hero = hud.party[0] if len(hud.party) >= 1 else None
    ally = hud.party[1] if len(hud.party) >= 2 else None
    anim = hud.anims[0] if hud.anims else None
    assets = use_assets()
    sprite_hud = (ally
      and (hud.draws_hp
        and assets.sprites["hud"]
        or assets.sprites["hud_town"]
      ) or (hud.draws_hp
        and assets.sprites["hud_single"]
        or assets.sprites["hud_circle"]
      )
    )

    width = sprite_hud.get_width() + 1
    height = sprite_hud.get_height()
    sprite = Surface((width, height), SRCALPHA)
    sprite.blit(sprite_hud, (0, 0))

    hero_portrait = None
    ally_portrait = None

    draws_portrait = portrait and hud.draws_portrait
    if draws_portrait:
      if (type(hero) is Knight and type(anim) is not SwitchOutAnim
      or type(ally) is Knight and type(anim) is SwitchOutAnim):
        hero_portrait = assets.sprites["circle_knight"]
      if (type(hero) is Mage and type(anim) is not SwitchOutAnim
      or type(ally) is Mage and type(anim) is SwitchOutAnim):
        hero_portrait = assets.sprites["circle_mage"]
      if (type(hero) is Rogue and type(anim) is not SwitchOutAnim
      or type(ally) is Rogue and type(anim) is SwitchOutAnim):
        hero_portrait = assets.sprites["circle_rogue"]

      if (type(ally) is Knight and type(anim) is not SwitchOutAnim
      or type(hero) is Knight and type(anim) is SwitchOutAnim):
        ally_portrait = assets.sprites["circ16_knight"]
      if (type(ally) is Mage and type(anim) is not SwitchOutAnim
      or type(hero) is Mage and type(anim) is SwitchOutAnim):
        ally_portrait = assets.sprites["circ16_mage"]
      if (type(ally) is Rogue and type(anim) is not SwitchOutAnim
      or type(hero) is Rogue and type(anim) is SwitchOutAnim):
        ally_portrait = assets.sprites["circ16_rogue"]

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
        hero_scaled = scale(hero_portrait, (int(hero_width), int(hero_height)))
        if ally:
          ally_width = lerp(ally_portrait.get_width(), 0, t)
          ally_height = lerp(ally_portrait.get_height(), 0, t)
          ally_scaled = scale(ally_portrait, (int(ally_width), int(ally_height)))
      sprite.blit(hero_scaled, (
        hero_portrait.get_width() // 2 - hero_scaled.get_width() // 2,
        hero_portrait.get_height() // 2 - hero_scaled.get_height() // 2
      ))

    def draw_bar(surface, pos, percent, color):
      surface.blit(render_bar(percent, color), pos)

    color_blink = CYAN if hud.time // 2 % 2 else DARKCYAN
    hero_hp_pos = (HP_BAR_X, HP_BAR_Y1)
    if hud.draws_hp:
      color_bg = DARKGREEN if hero.get_hp() > HP_CRITICAL else DARKYELLOW
      color_fg = LIME if hero.get_hp() > HP_CRITICAL else YELLOW
      if not hero.dead:
        draw_bar(sprite, hero_hp_pos, percent=1, color=color_bg)
      if hero.get_hp() <= hud.hp_hero:
        draw_bar(sprite, hero_hp_pos, percent=hud.hp_hero / hero.get_hp_max(), color=RED)
        draw_bar(sprite, hero_hp_pos, percent=hero.get_hp() / hero.get_hp_max(), color=color_fg)
      else:
        draw_bar(sprite, hero_hp_pos, percent=hero.get_hp() / hero.get_hp_max(), color=color_blink)
        draw_bar(sprite, hero_hp_pos, percent=hud.hp_hero / hero.get_hp_max(), color=color_fg)

    if ally:
      if draws_portrait:
        sprite.blit(ally_scaled, (
          CIRC16_X + ally_portrait.get_width() // 2 - ally_scaled.get_width() // 2,
          CIRC16_Y + ally_portrait.get_height() // 2 - ally_scaled.get_height() // 2
        ))
      ally_hp_pos = (HP_BAR_X, HP_BAR_Y2)
      if hud.draws_hp:
        color_bg = DARKGREEN if ally.get_hp() > HP_CRITICAL else DARKYELLOW
        color_fg = LIME if ally.get_hp() > HP_CRITICAL else YELLOW
        if not ally.dead:
          draw_bar(sprite, ally_hp_pos, percent=1, color=color_bg)
        if ally.get_hp() <= hud.hp_ally:
          draw_bar(sprite, ally_hp_pos, percent=hud.hp_ally / ally.get_hp_max(), color=RED)
          draw_bar(sprite, ally_hp_pos, percent=ally.get_hp() / ally.get_hp_max(), color=color_fg)
        else:
          draw_bar(sprite, ally_hp_pos, percent=ally.get_hp() / ally.get_hp_max(), color=color_blink)
          draw_bar(sprite, ally_hp_pos, percent=hud.hp_ally / ally.get_hp_max(), color=color_fg)

    if hud.draws_hp:
      sprite.blit(assets.sprites["hp"], (HP_X, HP_Y))
      hptext_image = render_numbers(hero.get_hp(), hero.get_hp_max(), crit_threshold=HP_CRITICAL, time=hud.time)
      sprite.blit(hptext_image, (HP_VALUE_X, HP_VALUE_Y))

    return sprite

  def view(hud, portrait=True):
    hud.image = hud.render(portrait)
    hud_x, hud_y = hud.pos
    anim = hud.anims[0] if hud.anims else None
    if anim:
      if type(anim) is FlinchAnim:
        offset_x, offset_y = hud.offset
        while (offset_x, offset_y) == hud.offset:
          offset_x = randint(-1, 1)
          offset_y = randint(-1, 1)
        hud_x += offset_x
        hud_y += offset_y
      elif type(anim) is SlideAnim:
        t = ease_in_out(anim.pos)
        (start_x, start_y), (target_x, target_y) = anim.target
        hud_x = lerp(start_x, target_x, t)
        hud_y = lerp(start_y, target_y, t)
    elif not hud.active:
      return []
    return [Sprite(
      image=hud.image,
      pos=(hud_x, hud_y),
      layer="hud"
    )]

def render_bar(percent, color):
  surface = Surface((HP_WIDTH, 3), SRCALPHA)
  pygame.draw.rect(surface, color, Rect(
    (0, 0),
    (ceil(HP_WIDTH // 2 * min(0.5, percent) / 0.5) - 1, 2)
  ))
  if percent > 0.5:
    pygame.draw.rect(surface, color, Rect(
      (HP_WIDTH // 2 - 1, 1),
      (HP_WIDTH // 2 * min(1, (percent - 0.5) / 0.5), 2)
    ))
  return surface

def render_numbers(hp, hp_max, crit_threshold=0, time=0):
  assets = use_assets()

  hp_text = str(ceil(max(0, hp)))
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

  sprite = Surface((sprite_width, sprite_height), SRCALPHA)

  if gray:
    sprite_firstno = replace_color(sprite_firstno, WHITE, GRAY)
  sprite.blit(sprite_firstno, (0, 0))

  x = sprite_firstno.get_width() - 1

  for char in hp_text[1:]:
    number = render_char(char, assets.fonts["numbers13"]).convert_alpha()
    color_blink = RED if time % 30 < 15 else DARKRED
    if hp <= crit_threshold:
      number = replace_color(number, BLACK, color_blink)
    sprite.blit(number, (x, HP_VALUE_Y))
    x += number.get_width() - 2

  sprite.blit(sprite_slash, (x, HP_MAX_Y))

  sprite_hpmax = outline(sprite_hpmax, BLACK)
  sprite_hpmax = outline(sprite_hpmax, WHITE)
  sprite.blit(sprite_hpmax, (HP_MAX_X, HP_MAX_Y))
  return sprite
