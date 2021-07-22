import random
import pygame
from pygame import Surface, Rect, SRCALPHA
from assets import load as use_assets
from filters import replace_color
from colors.palette import RED, WHITE, GOLD, VIOLET, GRAY

from anims import Anim
from anims.tween import TweenAnim
from anims.flicker import FlickerAnim
from easing.expo import ease_out
from lib.lerp import lerp

from dungeon.actors.eye import Eyeball
from dungeon.actors.mimic import Mimic

MARGIN = 8
HP_OVERLAP = 0
HP_OFFSET_X = 6
HP_OFFSET_Y = 15
ENTER_SPEED = 8
EXIT_SPEED = 8
BAR_PADDING_X = 3
BAR_PADDING_Y = 1
BAR_HEIGHT = 2
PORTRAIT_X = 23
PORTRAIT_Y = 3
DEPLETE_SPEED = 90

class FlinchAnim(Anim): pass

class Preview:
  def __init__(preview, actor):
    preview.actor = actor
    preview.sprite = None
    preview.x = 0
    preview.y = 0
    preview.width = -1
    preview.height = -1
    preview.hp = actor.get_hp()
    preview.hp_drawn = preview.hp
    preview.offset = (0, 0)
    preview.anim = None

  def update(preview):
    if preview.sprite is None or preview.hp != preview.actor.get_hp():
      preview.sprite = preview.render()
      if preview.actor.get_hp() < preview.hp_drawn:
        preview.anim = FlinchAnim(duration=10)
      preview.hp = max(preview.actor.get_hp(), preview.hp - preview.actor.get_hp_max() / DEPLETE_SPEED)
    preview.hp_drawn = preview.actor.get_hp()

    if preview.anim is None:
      return

    anim = preview.anim
    if type(anim) is FlinchAnim:
      offset_x, offset_y = preview.offset
      while (offset_x, offset_y) == preview.offset:
        offset_x = random.randint(-1, 1)
        offset_y = random.randint(-1, 1)
      preview.offset = (offset_x, offset_y)
      anim.update()
      if anim.done:
        offset = (0, 0)
        preview.anim = None
      if anim.done and preview.actor.get_hp() == 0:
        preview.anim = FlickerAnim(duration=30, target=preview)
    elif type(anim) is FlickerAnim:
      anim.update()

  def render(preview):
    actor = preview.actor
    assets = use_assets()
    base = assets.sprites["portrait_enemy"]
    portrait = None
    portrait_id = "portrait_" + actor.get_name().lower()
    if portrait_id in assets.sprites:
      portrait = assets.sprites[portrait_id]
    hp_tag = assets.sprites["tag_hp"]
    bar = assets.sprites["bar_small"]
    bar_x = HP_OFFSET_X + hp_tag.get_width() + 1
    bar_y = HP_OFFSET_Y + hp_tag.get_height() - bar.get_height()
    bar_width = (bar.get_width() - BAR_PADDING_X * 2)
    bar_bg_width = bar_width * preview.hp / actor.get_hp_max()
    bar_fg_width = bar_width * actor.get_hp() / actor.get_hp_max()
    bar_bg_rect = Rect(
      bar_x + BAR_PADDING_X,
      bar_y + BAR_PADDING_Y,
      bar_bg_width,
      BAR_HEIGHT
    )
    bar_fg_rect = Rect(
      bar_x + BAR_PADDING_X,
      bar_y + BAR_PADDING_Y,
      bar_fg_width,
      BAR_HEIGHT
    )
    anim = preview.anim
    if type(anim) is FlinchAnim:
      if anim.time <= 2:
        portrait = portrait and replace_color(portrait, WHITE, RED)
    if type(anim) is FlickerAnim:
      if anim.time % 4 >= 2 or anim.done:
        portrait = portrait and replace_color(portrait, WHITE, GRAY)
    elif actor.ailment == "sleep":
      portrait = portrait and replace_color(portrait, WHITE, VIOLET)
    elif actor.rare:
      portrait = portrait and replace_color(portrait, WHITE, GOLD)
    surface_width = bar_x + bar.get_width()
    surface_height = HP_OFFSET_Y + hp_tag.get_height()
    surface = Surface((surface_width, surface_height), SRCALPHA)
    surface.blit(base, (0, 0))
    if portrait is not None:
      surface.blit(portrait, (PORTRAIT_X, PORTRAIT_Y))
    surface.blit(hp_tag, (HP_OFFSET_X, HP_OFFSET_Y))
    surface.blit(bar, (bar_x, bar_y))
    pygame.draw.rect(surface, RED, bar_bg_rect)
    pygame.draw.rect(surface, WHITE, bar_fg_rect)
    return surface

  def draw(preview, window):
    sprite = preview.sprite
    x = window.get_width() - preview.x
    y = window.get_height() * 2 // 3 - sprite.get_height() // 2
    window.blit(sprite, (x, y))
