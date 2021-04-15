from assets import load as use_assets
from pygame import Surface, Rect
import pygame
import random

from anims import Anim
from anims.tween import TweenAnim
from easing.expo import ease_out
from lerp import lerp
import palette

MARGIN = 8
HP_OVERLAP = 0
HP_OFFSET_X = 6
HP_OFFSET_Y = 15
ENTER_SPEED = 8
EXIT_SPEED = 8
BAR_PADDING_X = 3
BAR_PADDING_Y = 1
BAR_HEIGHT = 2

class Preview:
  def __init__(preview, actor):
    preview.actor = actor
    preview.sprite = None
    preview.x = 0
    preview.hp = actor.hp
    preview.hp_prev = actor.hp
    preview.hp_time = 0
    preview.offset = (0, 0)
    preview.anim = None

  def update(preview):
    if preview.sprite is None or preview.hp != preview.actor.hp:
      preview.sprite = preview.render()
      if preview.hp == preview.hp_prev:
        preview.anim = Anim(duration=10)
      preview.hp = max(preview.actor.hp, preview.hp - 1 / 20)
    preview.hp_prev = preview.actor.hp

    if preview.anim:
      offset_x, offset_y = preview.offset
      while (offset_x, offset_y) == preview.offset:
        offset_x = random.randint(-1, 1)
        offset_y = random.randint(-1, 1)
      preview.offset = (offset_x, offset_y)
      anim = preview.anim
      anim.update()
      if anim.done:
        offset = (0, 0)
        preview.anim = None

  def render(preview):
    actor = preview.actor
    assets = use_assets()
    portrait = assets.sprites["portrait_eye"] # TODO: disambiguate based on type
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
    surface_width = bar_x + bar.get_width()
    surface_height = HP_OFFSET_Y + hp_tag.get_height()
    surface = Surface((surface_width, surface_height))
    surface.set_colorkey(0xFF00FF)
    surface.fill(0xFF00FF)
    surface.blit(portrait, (0, 0))
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
