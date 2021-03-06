from pygame import Rect
from easing.expo import ease_out
from lib.sprite import Sprite
from anims.tween import TweenAnim
from lib.filters import replace_color, outline, shadow_lite as shadow
from colors.palette import BLACK

from comps import Component
from comps.skill import Skill
import assets

import traceback


def render_badge(skill):
  icon = Skill.get_icon(skill)
  icon = outline(icon, BLACK)
  icon = shadow(icon, BLACK)
  badge = replace_color(assets.sprites["skill_badge"], (255, 0, 0), skill.color)
  badge.blit(icon, (7, 3))
  return badge

def render_label(text):
  label = assets.ttf["normal"].render(text)
  label = outline(label, BLACK)
  label = shadow(label, BLACK)
  return label

class BadgeAnim: pass
class BadgeEnterAnim(BadgeAnim, TweenAnim): duration = 12
class BadgeExitAnim(BadgeAnim, TweenAnim): duration = 6

class LabelAnim: pass
class LabelEnterAnim(LabelAnim, TweenAnim): duration = 12
class LabelExitAnim(LabelAnim, TweenAnim): duration = 6

class Miniskill(Component):
  def __init__(comp, skill=None, pos=(0, 0), *args, **kwargs):
    super().__init__(pos, *args, **kwargs)
    comp.skill = skill
    comp.anims = []
    comp.cached_badge = None
    comp.cached_label = None
    comp.active = False

  def reload(comp, skill, delay=0):
    comp.skill = skill
    if comp.active:
      comp.exit(on_end=lambda: comp.enter(delay=delay))
    else:
      comp.enter(delay=delay)

  def enter(comp, delay=0):
    comp.cached_badge = None
    comp.cached_label = None
    comp.active = True
    comp.exiting = False
    comp.anims += [
      BadgeEnterAnim(easing=ease_out, delay=delay),
      LabelEnterAnim(easing=ease_out, delay=delay + BadgeEnterAnim.duration // 2),
    ]

  def exit(comp, on_end=None):
    if next((a for a in comp.anims if isinstance(a, BadgeEnterAnim) and a.time < 0), None):
      return comp.force_exit()

    comp.exiting = True
    comp.anims += [
      BadgeExitAnim(),
      LabelExitAnim(),
    ]
    sorted(comp.anims, key=lambda a: a.duration + a.delay)[-1].on_end = lambda: (
      setattr(comp, "active", False),
      on_end and on_end(),
    )

  def force_exit(comp):
    comp.active = False
    comp.anims = []

  def update(comp):
    comp.anims = [a for a in comp.anims if not a.done and [a.update()]]

  def view(comp):
    if not comp.active:
      return []
    sprites = Sprite.move_all((
      comp.view_badge()
      + comp.view_label()
    ), comp.pos)
    for sprite in sprites:
      sprite.layer = "ui"
    return sprites

  def view_badge(comp):
    if not comp.cached_badge:
      if not comp.skill:
        return []
      comp.cached_badge = render_badge(skill=comp.skill)
    badge_image = comp.cached_badge
    badge_anim = next((a for a in comp.anims if isinstance(a, BadgeAnim)), None)
    badge_yscale = 1
    if type(badge_anim) is BadgeEnterAnim:
      badge_yscale = badge_anim.pos
    elif type(badge_anim) is BadgeExitAnim:
      badge_yscale = 1 - badge_anim.pos
    elif comp.exiting:
      return []
    return [Sprite(
      image=badge_image,
      origin=Sprite.ORIGIN_LEFT,
      size=(badge_image.get_width(), badge_image.get_height() * badge_yscale),
    )]

  def view_label(comp):
    if not comp.cached_label:
      if not comp.skill:
        return []
      comp.cached_label = render_label(text=comp.skill.name)
    label_image = comp.cached_label
    label_anim = next((a for a in comp.anims if isinstance(a, LabelAnim)), None)
    label_width = label_image.get_width()
    if type(label_anim) is LabelEnterAnim:
      label_width *= label_anim.pos
    elif type(label_anim) is LabelExitAnim:
      label_width *= 1 - label_anim.pos
    elif comp.exiting:
      return []
    label_image = label_image.subsurface(Rect(
      (label_image.get_width() - label_width, 0),
      (label_width, label_image.get_height())
    ))
    return [Sprite(
      image=label_image,
      pos=(comp.cached_badge.get_width() + 1, 0),
      origin=Sprite.ORIGIN_LEFT
    )]
