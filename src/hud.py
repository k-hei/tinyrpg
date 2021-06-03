import pygame
from pygame import Surface
from pygame.transform import scale

import palette
from assets import load as use_assets
from filters import replace_color

from cores.knight import KnightCore
from cores.mage import MageCore
from cores.rogue import RogueCore

from anims.tween import TweenAnim
from easing.expo import ease_out, ease_in
from lib.lerp import lerp

CIRC16_X = 29
CIRC16_Y = 26
ENTER_DURATION = 15
EXIT_DURATION = 8
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

  def __init__(panel):
    panel.sprite = None
    panel.active = True
    panel.anims = []
    panel.anims_drawn = 0
    panel.hero = None
    panel.ally = None
    panel.enter()

  def enter(panel):
    panel.active = True
    panel.anims.append(EnterAnim())

  def exit(panel):
    panel.active = False
    panel.anims.append(ExitAnim())

  def update(panel, hero, ally=None):
    if (panel.sprite is None
    or panel.anims_drawn
    or hero != panel.hero
    or ally != panel.ally):
      if hero != panel.hero:
        if panel.hero is not None:
          panel.anims.append(SwitchOutAnim())
          panel.anims.append(SwitchInAnim())
        panel.hero = hero
      if ally != panel.ally:
        panel.ally = ally
      anim = panel.anims[0] if panel.anims else None
      panel.anims_drawn = len(panel.anims)
      panel.sprite = panel.render(hero, ally, anim)
    return panel.sprite

  def render(panel, hero, ally, anim=None):
    assets = use_assets()
    sprite_hud = (ally
      and assets.sprites["hud_town"]
      or assets.sprites["hud_circle"])

    width = sprite_hud.get_width()
    height = sprite_hud.get_height()
    sprite = Surface((width, height)).convert_alpha()
    sprite.blit(sprite_hud, (0, 0))

    hero_portrait = None
    if (type(hero) is KnightCore and type(anim) is not SwitchOutAnim
    or type(ally) is KnightCore and type(anim) is SwitchOutAnim):
      hero_portrait = assets.sprites["circle_knight"]
    if (type(hero) is MageCore and type(anim) is not SwitchOutAnim
    or type(ally) is MageCore and type(anim) is SwitchOutAnim):
      hero_portrait = assets.sprites["circle_mage"]
    if (type(hero) is RogueCore and type(anim) is not SwitchOutAnim
    or type(ally) is RogueCore and type(anim) is SwitchOutAnim):
      hero_portrait = assets.sprites["circle_rogue"]

    ally_portrait = None
    if (type(ally) is KnightCore and type(anim) is not SwitchOutAnim
    or type(hero) is KnightCore and type(anim) is SwitchOutAnim):
      ally_portrait = assets.sprites["circ16_knight"]
    if (type(ally) is MageCore and type(anim) is not SwitchOutAnim
    or type(hero) is MageCore and type(anim) is SwitchOutAnim):
      ally_portrait = assets.sprites["circ16_mage"]
    if (type(ally) is RogueCore and type(anim) is not SwitchOutAnim
    or type(hero) is RogueCore and type(anim) is SwitchOutAnim):
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

  def draw(panel, surface, ctx):
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
