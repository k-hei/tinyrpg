from pygame import Surface, SRCALPHA
from assets import load as use_assets
from palette import BLACK, BLUE, GOLD
from filters import replace_color

class Control:
  def __init__(control, key, value):
    control.key = key
    control.value = value
    control.surface = None
    control.dirty = True
    control.pressed = {}
    for key in control.key:
      control.pressed[key] = False

  def press(control, key):
    if not control.pressed[key]:
      control.pressed[key] = True
      control.dirty = True

  def release(control, key):
    if control.pressed[key]:
      control.pressed[key] = False
      control.dirty = True

  def render(control):
    if control.surface and not control.dirty:
      return control.surface
    assets = use_assets()
    font = assets.ttf["roman"]
    nodes = []
    x = 0
    for key in control.key:
      icon_color = GOLD if control.pressed[key] else BLUE
      icon_image = assets.sprites["button_" + key.lower()]
      icon_image = replace_color(icon_image, BLACK, icon_color)
      nodes.append((icon_image, x))
      x += icon_image.get_width() + 2
    x += 2
    text_image = font.render(control.value)
    nodes.append((text_image, x))
    surface_width = x + text_image.get_width()
    surface_height = icon_image.get_height()
    if control.surface is None:
      control.surface = Surface((surface_width, surface_height), SRCALPHA)
    else:
      control.surface.fill(0)
    for image, x in nodes:
      y = surface_height // 2 - image.get_height() // 2
      control.surface.blit(image, (x, y))
    return control.surface
