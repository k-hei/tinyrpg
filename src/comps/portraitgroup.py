from sprite import Sprite
from config import WINDOW_WIDTH
from filters import darken as darken_image

class PortraitGroup:
  def __init__(group, portraits):
    group.portraits = portraits
    group.portrait_index = None

  def cycle(group):
    if group.portrait_index is None:
      group.portrait_index = 0
    else:
      group.portrait_index = (group.portrait_index + 1) % len(group.portraits)

  def view(group, sprites):
    portrait_sprites = []
    selection_sprites = []
    x = 0
    width = 0
    for i, portrait in enumerate(group.portraits):
      portrait_image = portrait.render()
      if group.portrait_index is not None and group.portrait_index != i:
        portrait_image = darken_image(portrait_image)
      portrait_sprite = Sprite(
        image=portrait_image,
        pos=(x, 128),
        origin=("left", "bottom")
      )
      if group.portrait_index == i:
        selection_sprites.append(portrait_sprite)
      else:
        portrait_sprites.append(portrait_sprite)
      portrait_width = portrait_image.get_width()
      width = x + portrait_width
      x += portrait_width - 64
    for sprite in portrait_sprites + selection_sprites:
      sprite.move((WINDOW_WIDTH - width + 16, 0))
    sprites += portrait_sprites + selection_sprites
