from pygame import Surface, SRCALPHA
from assets import load as use_assets
from colors.palette import BLACK, BLUE, GOLD
from filters import replace_color, darken_image

class Control:
  def __init__(control, key, value):
    control.key = key
    control.value = value
    control.surface = None
    control.dirty = True
    control.disabled = False
    control.pressed = {}
    for key in control.key:
      control.pressed[key] = False

  def press(control, key=None):
    if key:
      if not control.pressed[key]:
        control.pressed[key] = True
        control.dirty = True
    else:
      for key in control.pressed:
        control.pressed[key] = True
      control.dirty = True

  def release(control, key=None):
    if key:
      if control.pressed[key]:
        control.pressed[key] = False
        control.dirty = True
    else:
      for key in control.pressed:
        control.pressed[key] = False
      control.dirty = True

  def enable(control):
    if control.disabled:
      control.disabled = False
      control.dirty = True

  def disable(control):
    if not control.disabled:
      control.disabled = True
      control.dirty = True

  def render(control):
    if control.surface and not control.dirty:
      return control.surface
    assets = use_assets()
    font = assets.ttf["normal"]
    nodes = []
    x = 0
    for key in control.key:
      icon_color = GOLD if control.pressed[key] else BLUE
      icon_image = assets.sprites["button_" + key.lower()]
      icon_image = replace_color(icon_image, BLACK, icon_color)
      nodes.append((icon_image, x, 0))
      x += icon_image.get_width() + 2
    x += 2
    text_image = font.render(control.value)
    nodes.append((text_image, x, 1))
    surface_width = x + text_image.get_width()
    surface_height = icon_image.get_height()
    if control.surface is None:
      control.surface = Surface((surface_width, surface_height), SRCALPHA)
    else:
      control.surface.fill(0)
    for image, x, y in nodes:
      y += surface_height // 2 - image.get_height() / 2
      control.surface.blit(image, (x, y))
    if control.disabled:
      control.surface = darken_image(control.surface)
    return control.surface
