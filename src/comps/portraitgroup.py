from sprite import Sprite
from config import WINDOW_WIDTH
from filters import darken as darken_image
from anims.tween import TweenAnim
from lib.lerp import lerp
from easing.circ import ease_out
from easing.expo import ease_in_out

class EnterAnim(TweenAnim): pass
class ExitAnim(TweenAnim): pass
class CycleAnim(TweenAnim): pass

PORTRAIT_OVERLAP = 64
OFFSET_STATIC = 32
OFFSET_CYCLING = 64

def cycle_list(items, delta=1):
  if delta == 1:
    items.insert(0, items.pop())
  elif delta == -1:
    items.append(items.pop(0))

class PortraitGroup:
  def get_portraits_width(images):
    width = 0
    x = 0
    for image in images:
      width = x + image.get_width()
      x += image.get_width() - PORTRAIT_OVERLAP
    return width

  def get_portraits_xs(images, cycling=False):
    width = PortraitGroup.get_portraits_width(images)
    xs = []
    x = 0
    offset = (OFFSET_CYCLING if cycling else OFFSET_STATIC) if len(images) > 1 else 0
    for image in images:
      xs.append(x + WINDOW_WIDTH - width + offset)
      x += image.get_width() - PORTRAIT_OVERLAP
    return xs

  def __init__(group, portraits):
    group.portraits = portraits
    group.portraits_init = list(portraits)
    group.cycling = False
    group.exiting = False
    group.anims = []
    group.anims_xs = {}
    group.on_animate = None

  def enter(group, on_end=None):
    for i, portrait in enumerate(group.portraits):
      group.anims.append(EnterAnim(
        duration=30,
        delay=i * 15,
        target=portrait
      ))
    group.on_animate = on_end

  def exit(group, on_end=None):
    for i, portrait in enumerate(reversed(group.portraits)):
      group.anims.append(ExitAnim(
        duration=10,
        delay=i * 4,
        target=portrait
      ))
    group.on_animate = on_end
    group.exiting = True

  def cycle(group):
    portraits_images = list(map(lambda portrait: portrait.render(), group.portraits))
    from_xs = PortraitGroup.get_portraits_xs(portraits_images, cycling=group.cycling)
    cycle_list(portraits_images)
    cycle_list(group.portraits)
    to_xs = PortraitGroup.get_portraits_xs(portraits_images, cycling=True)
    cycle_list(to_xs)
    xs = list(zip(from_xs, to_xs))
    cycle_list(xs)
    for i, portrait in enumerate(group.portraits):
      group.anims.append(CycleAnim(
        duration=15,
        target=portrait
      ))
      group.anims_xs[portrait] = xs[i]
    group.cycling = True

  def stop_cycle(group):
    portrait_imagemap = dict(map(lambda portrait: (portrait, portrait.render()), group.portraits))
    portrait_images = portrait_imagemap.values()
    from_xs = dict(zip(
      group.portraits,
      PortraitGroup.get_portraits_xs(portrait_images, group.cycling)
    ))
    group.cycling = False
    group.portraits = list(group.portraits_init)
    portrait_images = list(map(lambda portrait: portrait_imagemap[portrait], group.portraits))
    to_xs = dict(zip(
      group.portraits,
      PortraitGroup.get_portraits_xs(portrait_images, cycling=False)
    ))
    for i, portrait in enumerate(group.portraits):
      group.anims.append(CycleAnim(
        duration=15,
        target=portrait
      ))
      group.anims_xs[portrait] = (from_xs[portrait], to_xs[portrait])

  def update(group):
    for anim in group.anims:
      if anim.done:
        group.anims.remove(anim)
        if not group.anims and group.on_animate:
          group.on_animate()
          group.on_animate = None
      else:
        anim.update()

  def view(group, sprites):
    selection_sprites = []
    portraits_sprites = []
    portraits_images = list(map(lambda portrait: portrait.render(), group.portraits))
    portraits_xs = PortraitGroup.get_portraits_xs(portraits_images, group.cycling)

    for i, portrait in enumerate(group.portraits):
      portrait_image = portraits_images[i]
      if group.cycling and i != 0:
        portrait_image = darken_image(portrait_image)
      portrait_anim = next((a for a in group.anims if a.target is portrait), None)
      portrait_x = portraits_xs[i]
      if type(portrait_anim) is EnterAnim:
        t = portrait_anim.pos
        t = ease_out(t)
        portrait_x = lerp(WINDOW_WIDTH, portrait_x, t)
      elif type(portrait_anim) is ExitAnim:
        t = portrait_anim.pos
        portrait_x = lerp(portrait_x, WINDOW_WIDTH, t)
      elif type(portrait_anim) is CycleAnim:
        t = portrait_anim.pos
        t = ease_in_out(t)
        from_x, to_x = group.anims_xs[portrait]
        portrait_x = lerp(from_x, to_x, t)
      elif group.exiting:
        continue
      portrait_sprite = Sprite(
        image=portrait_image,
        pos=(portrait_x, 128),
        origin=("left", "bottom")
      )
      if group.cycling and i == 0:
        selection_sprites.append(portrait_sprite)
      else:
        portraits_sprites.append(portrait_sprite)
    sprites += portraits_sprites + selection_sprites
