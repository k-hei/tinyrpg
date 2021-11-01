from lib.sprite import Sprite
from config import WINDOW_WIDTH
from lib.filters import darken_image
from anims.tween import TweenAnim
from lib.lerp import lerp
from easing.circ import ease_out
from easing.expo import ease_in_out

class EnterAnim(TweenAnim): pass
class ExitAnim(TweenAnim): pass
class CycleAnim(TweenAnim): pass
class HSlideAnim(TweenAnim): duration = 30
class VSlideAnim(TweenAnim): duration = 30

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
      xs.append(x + WINDOW_WIDTH - width + offset +  image.get_width() / 2)
      x += image.get_width() - PORTRAIT_OVERLAP
    return xs

  def __init__(group, portraits):
    group.portraits = portraits
    group.portraits_init = list(portraits)
    group.portraits_cache = {}
    group.portraits_xs = []
    group.selected = None
    group.cycling = False
    group.exiting = False
    group.y = 128
    group.anims = []
    group.anims_xs = {}
    group.on_animate = None

  @property
  def y(group):
    return group._y

  @y.setter
  def y(group, y):
    if "_y" in dir(group):
      group.anims.append(VSlideAnim(target=(group._y, y)))
    group._y = y

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

  def slide(group, index, x, duration=0):
    portrait = group.portraits[index]
    group.anims.append(HSlideAnim(target=portrait, duration=duration))
    group.anims_xs[portrait] = (group.portraits_xs[index], x)
    group.portraits_xs[index] = x

  def select(group, index):
    group.selected = index
    for i, portrait in enumerate(group.portraits):
      if i == index:
        portrait.undarken()
      else:
        portrait.darken()

  def deselect(group):
    group.selected = None
    for portrait in group.portraits:
      portrait.undarken()

  def update(group):
    for anim in group.anims:
      if anim.done:
        group.anims.remove(anim)
        if not group.anims and group.on_animate:
          group.on_animate()
          group.on_animate = None
      else:
        anim.update()

  def view(group):
    sprites = []
    selection_sprites = []
    portraits_sprites = []
    portraits_images = list(map(lambda portrait: portrait.render(), group.portraits))
    if not group.portraits_xs:
      group.portraits_xs = PortraitGroup.get_portraits_xs(portraits_images, group.cycling)
    portraits_xs = group.portraits_xs

    group_y = group.y
    slide_anim = next((a for a in group.anims if isinstance(a, VSlideAnim)), None)
    if slide_anim:
      start_y, goal_y = slide_anim.target
      group_y = lerp(start_y, goal_y, t=ease_in_out(slide_anim.pos))

    for i, portrait in enumerate(group.portraits):
      portrait_image = portraits_images[i]
      if group.cycling and i != 0:
        if i not in group.portraits_cache:
          group.portraits_cache[i] = darken_image(portrait_image)
        portrait_image = group.portraits_cache[i]
      portrait_anim = next((a for a in group.anims if a.target is portrait), None)
      portrait_x = portraits_xs[i]
      portrait_xstart = WINDOW_WIDTH + portrait_image.get_width() / 2
      if type(portrait_anim) is EnterAnim:
        t = portrait_anim.pos
        t = ease_out(t)
        portrait_x = lerp(portrait_xstart, portrait_x, t)
      elif type(portrait_anim) is ExitAnim:
        t = portrait_anim.pos
        portrait_x = lerp(portrait_x, portrait_xstart, t)
      elif type(portrait_anim) is CycleAnim or type(portrait_anim) is HSlideAnim:
        t = portrait_anim.pos
        t = ease_in_out(t)
        from_x, to_x = group.anims_xs[portrait]
        portrait_x = lerp(from_x, to_x, t)
      elif group.exiting:
        continue
      portrait_sprite = Sprite(
        image=portrait_image,
        pos=(portrait_x, group_y),
        origin=Sprite.ORIGIN_BOTTOM,
      )
      if group.cycling and i == 0 or i == group.selected:
        selection_sprites.append(portrait_sprite)
      else:
        portraits_sprites.append(portrait_sprite)
    sprites += portraits_sprites + selection_sprites
    return sprites
