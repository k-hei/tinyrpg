from lib.filters import replace_color
from colors.palette import WHITE, ORANGE, DARKORANGE

class Portrait:
  BLINK_INTERVAL = 150

  def __init__(portrait):
    portrait.talking = False
    portrait.dark = False
    portrait.ticks = 0
    portrait.anims = []
    portrait.image_cache = None

  def blink(portrait):
    pass

  def darken(portrait):
    portrait.dark = True

  def undarken(portrait):
    portrait.dark = False

  def start_talk(portrait):
    portrait.talking = True

  def stop_talk(portrait):
    portrait.talking = False

  def update(portrait):
    for anim in portrait.anims:
      if anim.done:
        portrait.anims.remove(anim)
      else:
        anim.update()
    portrait.ticks += 1
    if portrait.ticks % Portrait.BLINK_INTERVAL == 0:
      portrait.blink()

  def render(portrait, image):
    portrait.update()
    if not portrait.image_cache:
      portrait.image_cache = (
        portrait_image := replace_color(image, WHITE, ORANGE),
        portrait_image_dark := replace_color(image, WHITE, DARKORANGE)
      )
    portrait_image, portrait_image_dark = portrait.image_cache
    return portrait_image if not portrait.dark else portrait_image_dark
