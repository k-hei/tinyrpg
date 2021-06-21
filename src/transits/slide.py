from transits import Transit
from config import WINDOW_HEIGHT

class SlideDown(Transit):
  duration = 15

  def __init__(transit, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def update(transit):
    if transit.done:
      return
    if transit.time == transit.duration:
      transit.done = True
      if transit.on_end:
        transit.on_end()
    else:
      transit.time += 1

  def view(transit, sprites):
    t = transit.time / transit.duration
    y = WINDOW_HEIGHT * t
    for sprite in sprites:
      if sprite.layer != "hud":
        sprite.move((0, y))
    return []
