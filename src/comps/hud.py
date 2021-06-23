from math import ceil
import pygame
from pygame import Surface, SRCALPHA
from pygame.transform import scale

from palette import BLACK, WHITE, BLUE, RED, CYAN, GRAY
from assets import load as use_assets
from filters import replace_color, recolor, outline
from sprite import Sprite
from text import render_char, render as render_text, find_width as find_text_width

from cores.knight import Knight
from cores.mage import Mage
from cores.rogue import Rogue

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
class SwitchOutAnim(TweenAnim):
  def __init__(anim):
    super().__init__(duration=SWITCHOUT_DURATION)
class SwitchInAnim(TweenAnim):
  def __init__(anim):
    super().__init__(duration=SWITCHIN_DURATION)

class Hud:
  MARGIN_LEFT = 8
  MARGIN_TOP = 8

  def __init__(hud, party):
    hud.party = party
    hud.image = None
    hud.active = True
    hud.anims = []
    hud.anims_drawn = 0
    hud.hero = None
    hud.ally = None
    hud.enter()

  def enter(hud):
    hud.active = True
    hud.anims.append(EnterAnim())

  def exit(hud):
    hud.active = False
    hud.anims.append(ExitAnim())

  def update(hud):
    hero = hud.party[0]
    ally = hud.party[1] if len(hud.party) == 2 else None
    if (hud.image is None
    or hud.anims_drawn
    or hero != hud.hero
    or ally != hud.ally):
      if hero != hud.hero:
        if hud.hero is not None:
          hud.anims.append(SwitchOutAnim())
          hud.anims.append(SwitchInAnim())
        hud.hero = hero
      if ally != hud.ally:
        hud.ally = ally
      anim = hud.anims[0] if hud.anims else None
      hud.anims_drawn = len(hud.anims)
      hud.image = hud.render(hero, ally, anim)
    return hud.image

  def render(hud, hero, ally, anim=None):
    assets = use_assets()
    sprite_hud = (ally
      and assets.sprites["hud_town"]
      or assets.sprites["hud_circle"])

    width = sprite_hud.get_width()
    height = sprite_hud.get_height()
    sprite = Surface((width, height)).convert_alpha()
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
      hero_portrait = replace_color(hero_portrait, palette.WHITE, palette.BLACK)
      hero_portrait = replace_color(hero_portrait, palette.BLUE, palette.RED)
    if ally and ally.dead:
      ally_portrait = replace_color(ally_portrait, palette.WHITE, palette.BLACK)
      ally_portrait = replace_color(ally_portrait, palette.BLUE, palette.RED)

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
    if ally:
      sprite.blit(ally_scaled, (
        CIRC16_X + ally_portrait.get_width() // 2 - ally_scaled.get_width() // 2,
        CIRC16_Y + ally_portrait.get_height() // 2 - ally_scaled.get_height() // 2
      ))
    return sprite

  def view(hud):
    hud.update()
    hud_image = hud.image
    hidden_x, hidden_y = Hud.MARGIN_LEFT, -hud_image.get_height()
    corner_x, corner_y = Hud.MARGIN_LEFT, Hud.MARGIN_TOP
    anim = hud.anims[0] if hud.anims else None
    if anim:
      t = anim.update()
      if type(anim) is EnterAnim:
        t = ease_out(t)
        start_x, start_y = hidden_x, hidden_y
        target_x, target_y = corner_x, corner_y
      elif type(anim) is ExitAnim:
        start_x, start_y = corner_x, corner_y
        target_x, target_y = hidden_x, hidden_y
      else:
        hud_x = corner_x
        hud_y = corner_y

      if type(anim) is EnterAnim or type(anim) is ExitAnim:
        hud_x = lerp(start_x, target_x, t)
        hud_y = lerp(start_y, target_y, t)

      if anim.done:
        hud.anims.pop(0)
    elif hud.active:
      hud_x = corner_x
      hud_y = corner_y
    else:
      return []
    return [Sprite(
      image=hud_image,
      pos=(hud_x, hud_y),
      layer="hud"
    )]

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
