from pygame import Rect
from easing.expo import ease_out
from lib.sprite import Sprite
from anims.tween import TweenAnim
from lib.filters import replace_color, outline, shadow_lite as shadow
from colors.palette import BLACK

from comps import Component
from comps.skill import Skill
import assets

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
class BadgeEnterAnim(BadgeAnim, TweenAnim): duration = 15
class BadgeExitAnim(BadgeAnim, TweenAnim): duration = 7

class LabelAnim: pass
class LabelEnterAnim(LabelAnim, TweenAnim): duration = 15
class LabelExitAnim(LabelAnim, TweenAnim): duration = 7

class Miniskill(Component):
  def __init__(comp, skill, *args, **kwargs):
    super().__init__(*args, **kwargs)
    comp.skill = skill
    comp.anims = []
    comp.cached_badge = None
    comp.cached_label = None

  def reload(comp, skill, delay=0):
    comp.skill = skill
    comp.enter(delay=delay)

  def enter(comp, delay=0):
    comp.active = True
    comp.exiting = False
    comp.cached_badge = render_badge(skill=comp.skill)
    comp.cached_label = render_label(text=comp.skill.name)
    comp.anims = [
      BadgeEnterAnim(easing=ease_out, delay=delay),
      LabelEnterAnim(easing=ease_out, delay=delay + BadgeEnterAnim.duration // 2),
    ]

  def exit(comp, on_end=None):
    comp.active = False
    comp.exiting = True
    comp.anims = [
      BadgeExitAnim(),
      LabelExitAnim(),
    ]
    sorted(comp.anims, key=lambda a: a.duration + a.delay)[0].on_end = on_end

  def update(comp):
    comp.anims = [a for a in comp.anims if not a.done and [a.update()]]

  def view(comp):
    sprites = Sprite.move_all((
      comp.view_badge()
      + comp.view_label()
    ), comp.pos)
    for sprite in sprites:
      sprite.layer = "ui"
    return sprites

  def view_badge(comp):
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
      pos=(comp.cached_badge.get_width() + 2, 0),
      origin=Sprite.ORIGIN_LEFT
    )]
