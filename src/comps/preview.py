from assets import load as use_assets
from pygame import Surface, Rect
import pygame

from anims.tween import TweenAnim
from easing.expo import ease_out
from lerp import lerp

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
    preview.side = "right"
    preview.active = True
    preview.anim = None
    preview.done = False

  def enter(preview, on_end=None):
    preview.active = True
    preview.anim = TweenAnim(duration=30, on_end=on_end)

  def exit(preview, on_end=None):
    preview.active = False
    preview.anim = TweenAnim(duration=30, on_end=on_end)

  def update(preview):
    if preview.sprite is None or preview.hp != preview.actor.hp:
      preview.sprite = preview.render()
      preview.hp = preview.actor.hp
    if preview.anim:
      anim = preview.anim
      t = anim.update()
      if preview.active:
        t = ease_out(t)
      else:
        t = 1 - t
      start_x = 0
      end_x = MARGIN + preview.sprite.get_width()
      preview.x = lerp(start_x, end_x, t)
      if anim.done:
        print(preview, "done")
        if anim.on_end:
          anim.on_end()
        preview.anim = None

  def render(preview):
    actor = preview.actor
    assets = use_assets()
    portrait = assets.sprites["portrait_eye"] # TODO: disambiguate based on type
    hp_tag = assets.sprites["tag_hp"]
    bar = assets.sprites["bar_small"]
    bar_x = HP_OFFSET_X + hp_tag.get_width() + 1
    bar_y = HP_OFFSET_Y + hp_tag.get_height() - bar.get_height()
    bar_width = (bar.get_width() - BAR_PADDING_X * 2) * actor.hp / actor.hp_max
    bar_rect = Rect(
      bar_x + BAR_PADDING_X,
      bar_y + BAR_PADDING_Y,
      bar_width,
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
    pygame.draw.rect(surface, 0xFFFFFF, bar_rect)
    return surface

  def draw(preview, window):
    sprite = preview.sprite
    x = window.get_width() - preview.x
    y = window.get_height() * 2 // 3 - sprite.get_height() // 2
    window.blit(sprite, (x, y))
