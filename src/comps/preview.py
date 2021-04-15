import random
import pygame
from pygame import Surface, Rect
from assets import load as use_assets
from filters import replace_color
import palette

from anims import Anim
from anims.tween import TweenAnim
from anims.flicker import FlickerAnim
from easing.expo import ease_out
from lerp import lerp

from actors.eye import Eye
from actors.mimic import Mimic

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

class ShakeAnim(Anim): pass

class Preview:
  def __init__(preview, actor):
    preview.actor = actor
    preview.sprite = None
    preview.x = 0
    preview.y = 0
    preview.width = -1
    preview.height = -1
    preview.hp = actor.hp
    preview.hp_prev = actor.hp
    preview.hp_time = 0
    preview.offset = (0, 0)
    preview.anim = None

  def update(preview):
    if preview.sprite is None or preview.hp != preview.actor.hp:
      preview.sprite = preview.render()
      if preview.hp == preview.hp_prev:
        preview.anim = ShakeAnim(duration=10)
      preview.hp = max(preview.actor.hp, preview.hp - 1 / 20)
    preview.hp_prev = preview.actor.hp

    if preview.anim is None:
      return

    anim = preview.anim
    if type(anim) is ShakeAnim:
      offset_x, offset_y = preview.offset
      while (offset_x, offset_y) == preview.offset:
        offset_x = random.randint(-1, 1)
        offset_y = random.randint(-1, 1)
      preview.offset = (offset_x, offset_y)
      anim.update()
      if anim.done:
        offset = (0, 0)
        preview.anim = None
      if anim.done and preview.actor.hp == 0:
        preview.anim = FlickerAnim(duration=30, target=preview)
    elif type(anim) is FlickerAnim:
      anim.update()

  def render(preview):
    actor = preview.actor
    assets = use_assets()
    base = assets.sprites["portrait_enemy"]
    portrait = None
    if type(actor) is Eye:
      portrait = assets.sprites["portrait_eye"]
    elif type(actor) is Mimic:
      portrait = assets.sprites["portrait_mimic"]
    hp_tag = assets.sprites["tag_hp"]
    bar = assets.sprites["bar_small"]
    bar_x = HP_OFFSET_X + hp_tag.get_width() + 1
    bar_y = HP_OFFSET_Y + hp_tag.get_height() - bar.get_height()
    bar_width = (bar.get_width() - BAR_PADDING_X * 2)
    bar_bg_width = bar_width * preview.hp / actor.hp_max
    bar_fg_width = bar_width * actor.hp / actor.hp_max
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
    if type(anim) is FlickerAnim and (anim.time % 4 >= 2 or anim.done):
      portrait = portrait and replace_color(portrait, palette.WHITE, palette.GRAY)
    elif type(anim) is ShakeAnim and anim.time <= 2:
      portrait = portrait and replace_color(portrait, palette.WHITE, palette.RED)
    elif actor.asleep:
      portrait = portrait and replace_color(portrait, palette.WHITE, palette.PURPLE)
    surface_width = bar_x + bar.get_width()
    surface_height = HP_OFFSET_Y + hp_tag.get_height()
    surface = Surface((surface_width, surface_height))
    surface.set_colorkey(0xFF00FF)
    surface.fill(0xFF00FF)
    surface.blit(base, (0, 0))
    if portrait is not None:
      surface.blit(portrait, (PORTRAIT_X, PORTRAIT_Y))
    surface.blit(hp_tag, (HP_OFFSET_X, HP_OFFSET_Y))
    surface.blit(bar, (bar_x, bar_y))
    pygame.draw.rect(surface, palette.RED, bar_bg_rect)
    pygame.draw.rect(surface, 0xFFFFFF, bar_fg_rect)
    return surface

  def draw(preview, window):
    sprite = preview.sprite
    x = window.get_width() - preview.x
    y = window.get_height() * 2 // 3 - sprite.get_height() // 2
    window.blit(sprite, (x, y))
