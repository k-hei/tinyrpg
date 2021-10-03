from math import ceil, inf
from random import randint
import pygame
from pygame import Rect, Surface, SRCALPHA
from pygame.transform import scale

from colors.palette import BLACK, WHITE, BLUE, RED, CYAN, GRAY
from assets import load as use_assets
from lib.filters import replace_color, recolor, outline
from sprite import Sprite
from text import render_char, render as render_text, find_width as find_text_width

from cores.knight import Knight
from cores.mage import Mage
from cores.rogue import Rogue

from anims import Anim
from anims.tween import TweenAnim
from easing.expo import ease_out, ease_in
from lib.lerp import lerp

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
class SwitchOutAnim(TweenAnim):
  def __init__(anim):
    super().__init__(duration=SWITCHOUT_DURATION)
class SwitchInAnim(TweenAnim):
  def __init__(anim):
    super().__init__(duration=SWITCHIN_DURATION)
class FlinchAnim(Anim):
  def __init__(anim):
    super().__init__(duration=FLINCH_DURATION)

class Hud:
  MARGIN_LEFT = 8
  MARGIN_TOP = 8

  def __init__(hud, party, hp=False):
    hud.party = party
    hud.draws_hp = hp
    hud.image = None
    hud.active = True
    hud.anims = []
    hud.offset = (0, 0)
    hud.hero = None
    hud.ally = None
    hud.hp_hero = inf
    hud.hp_ally = inf
    hud.hp_hero_drawn = inf
    hud.hp_ally_drawn = inf
    hud.enter()

  def enter(hud):
    hud.active = True
    hud.anims.append(EnterAnim())

  def exit(hud):
    hud.active = False
    hud.anims.append(ExitAnim())

  def update(hud):
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
          hud.anims.append(SwitchOutAnim())
          hud.anims.append(SwitchInAnim())
        hud.hero = hero
        hud.hp_hero = hero.get_hp()
      elif hero.get_hp() < hud.hp_hero_drawn:
        hud.anims.append(FlinchAnim())
        if hud.hp_hero == inf:
          hud.hp_hero = hero.get_hp_max()
      if ally != hud.ally:
        hud.ally = ally
        if ally:
          hud.hp_ally = ally.get_hp()
      elif ally and ally.get_hp() < hud.hp_ally_drawn:
        hud.anims.append(FlinchAnim())
        if hud.hp_ally == inf:
          hud.hp_ally = ally.get_hp_max()
      anim = hud.anims[0] if hud.anims else None
      if anim:
        if anim.done:
          hud.anims.pop(0)
        else:
          anim.update()
      if anim is None and hud.hp_hero > hero.get_hp():
        hud.hp_hero = max(hero.get_hp(), hud.hp_hero - hero.get_hp_max() / SPEED_DEPLETE)
      if anim is None and hud.hp_hero < hero.get_hp():
        hud.hp_hero = min(hero.get_hp(), hud.hp_hero + hero.get_hp_max() / SPEED_RESTORE)
      if anim is None and ally and hud.hp_ally > ally.get_hp():
        hud.hp_ally = max(ally.get_hp(), hud.hp_ally - ally.get_hp_max() / SPEED_DEPLETE)
      if anim is None and ally and hud.hp_ally < ally.get_hp():
        hud.hp_ally = min(ally.get_hp(), hud.hp_ally + ally.get_hp_max() / SPEED_RESTORE)
    hud.hp_hero_drawn = hero.get_hp()
    if ally:
      hud.hp_ally_drawn = ally.get_hp()

  def render(hud):
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
    if (type(hero) is Knight and type(anim) is not SwitchOutAnim
    or type(ally) is Knight and type(anim) is SwitchOutAnim):
      hero_portrait = assets.sprites["circle_knight"]
    if (type(hero) is Mage and type(anim) is not SwitchOutAnim
    or type(ally) is Mage and type(anim) is SwitchOutAnim):
      hero_portrait = assets.sprites["circle_mage"]
    if (type(hero) is Rogue and type(anim) is not SwitchOutAnim
    or type(ally) is Rogue and type(anim) is SwitchOutAnim):
      hero_portrait = assets.sprites["circle_rogue"]

    ally_portrait = None
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
    hero_hp_pos = (HP_BAR_X, HP_BAR_Y1)
    if hud.draws_hp and hero.get_hp() <= hud.hp_hero:
      sprite.blit(render_bar(hud.hp_hero / hero.get_hp_max(), RED), hero_hp_pos)
      sprite.blit(render_bar(hero.get_hp() / hero.get_hp_max(), WHITE), hero_hp_pos)
    else:
      sprite.blit(render_bar(hero.get_hp() / hero.get_hp_max(), CYAN), hero_hp_pos)
      sprite.blit(render_bar(hud.hp_hero / hero.get_hp_max(), WHITE), hero_hp_pos)

    if ally:
      sprite.blit(ally_scaled, (
        CIRC16_X + ally_portrait.get_width() // 2 - ally_scaled.get_width() // 2,
        CIRC16_Y + ally_portrait.get_height() // 2 - ally_scaled.get_height() // 2
      ))
      ally_hp_pos = (HP_BAR_X, HP_BAR_Y2)
      if hud.draws_hp and ally.get_hp() <= hud.hp_ally:
        sprite.blit(render_bar(hud.hp_ally / ally.get_hp_max(), RED), ally_hp_pos)
        sprite.blit(render_bar(ally.get_hp() / ally.get_hp_max(), WHITE), ally_hp_pos)
      else:
        sprite.blit(render_bar(ally.get_hp() / ally.get_hp_max(), CYAN), ally_hp_pos)
        sprite.blit(render_bar(hud.hp_ally / ally.get_hp_max(), WHITE), ally_hp_pos)

    if hud.draws_hp:
      sprite.blit(assets.sprites["hp"], (HP_X, HP_Y))
      hptext_image = render_numbers(hero.get_hp(), hero.get_hp_max(), HP_CRITICAL)
      sprite.blit(hptext_image, (HP_VALUE_X, HP_VALUE_Y))
    return sprite

  def view(hud):
    hud.image = hud.render()
    hud.update()
    from_x, from_y = Hud.MARGIN_LEFT, -hud.image.get_height()
    to_x, to_y = Hud.MARGIN_LEFT, Hud.MARGIN_TOP
    anim = hud.anims[0] if hud.anims else None
    if anim:
      if type(anim) is EnterAnim:
        t = anim.pos
        t = ease_out(t)
        start_x, start_y = from_x, from_y
        target_x, target_y = to_x, to_y
      elif type(anim) is ExitAnim:
        t = anim.pos
        start_x, start_y = to_x, to_y
        target_x, target_y = from_x, from_y
      elif type(anim) is FlinchAnim:
        offset_x, offset_y = hud.offset
        while (offset_x, offset_y) == hud.offset:
          offset_x = randint(-1, 1)
          offset_y = randint(-1, 1)
        hud_x = to_x + offset_x
        hud_y = to_y + offset_y
      else:
        hud_x = to_x
        hud_y = to_y
      if type(anim) is EnterAnim or type(anim) is ExitAnim:
        hud_x = lerp(start_x, target_x, t)
        hud_y = lerp(start_y, target_y, t)
    elif hud.active:
      hud_x = to_x
      hud_y = to_y
    else:
      return []
    return [Sprite(
      image=hud.image,
      pos=(hud_x, hud_y),
      layer="hud"
    )]

def render_bar(pct, color):
  surface = Surface((HP_WIDTH, 2), SRCALPHA)
  pygame.draw.rect(surface, color, Rect(
    (0, 0),
    (ceil(HP_WIDTH // 2 * min(0.5, pct) / 0.5 - 1), 1)
  ))
  if pct > 0.5:
    pygame.draw.rect(surface, color, Rect(
      (HP_WIDTH // 2 - 1, 1),
      (HP_WIDTH // 2 * min(1, (pct - 0.5) / 0.5), 1)
    ))
  return surface

def render_numbers(hp, hp_max, crit_threshold=0):
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
    if hp <= crit_threshold:
      number = replace_color(number, BLACK, RED)
    sprite.blit(number, (x, HP_VALUE_Y))
    x += number.get_width() - 2

  sprite.blit(sprite_slash, (x, HP_MAX_Y))

  sprite_hpmax = outline(sprite_hpmax, BLACK)
  sprite_hpmax = outline(sprite_hpmax, WHITE)
  sprite.blit(sprite_hpmax, (HP_MAX_X, HP_MAX_Y))
  return sprite
