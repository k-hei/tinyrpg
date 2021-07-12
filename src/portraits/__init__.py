from filters import replace_color
from colors.palette import WHITE, ORANGE

class Portrait:
  BLINK_INTERVAL = 150

  def __init__(portrait):
    portrait.talking = False
    portrait.ticks = 0
    portrait.anims = []

  def blink(portrait):
    pass

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
    return replace_color(image, WHITE, ORANGE)
