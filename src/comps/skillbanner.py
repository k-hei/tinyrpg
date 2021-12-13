from comps import Component
from anims.tween import TweenAnim
from anims.pause import PauseAnim
from lib.sprite import Sprite
from lib.filters import replace_color
import assets
from config import WINDOW_WIDTH, WINDOW_HEIGHT

BANNER_COLOR = (255, 0, 0)

class EnterAnim(TweenAnim): pass
class ExitAnim(TweenAnim): pass

class SkillBanner(Component):
  duration = 120

  def __init__(banner, *args, **kwargs):
    super().__init__(*args, **kwargs)
    banner.anims = []
    banner.image = None
    banner.image_written = None

  def enter(banner, text, color):
    banner.anims = [
      EnterAnim(duration=15),
      PauseAnim(duration=90),
      ExitAnim(duration=8),
    ]
    banner.image = replace_color(assets.sprites["skill_banner"], BANNER_COLOR, color)
    banner.image_written = Sprite(
      image=assets.ttf["english"].render(text),
      pos=(banner.image.get_width() // 2, banner.image.get_height() // 2),
      origin=("center", "center"),
    ).draw(banner.image.copy())
    banner.done = False

  def exit(banner):
    if len(banner.anims) > 1:
      banner.anims = [banner.anims[-1]]

  def update(banner):
    if not banner.anims:
      return

    anim = banner.anims[0]
    if anim.done:
      banner.anims.remove(anim)
    else:
      anim.update()

    if not banner.anims:
      banner.done = True

  def view(banner):
    if banner.done or not banner.image:
      return []
    banner_anim = banner.anims and banner.anims[0]
    banner_height = banner.image.get_height()
    if banner_anim:
      if type(banner_anim) is EnterAnim:
        banner_height *= banner_anim.pos
      elif type(banner_anim) is ExitAnim:
        banner_height *= (1 - banner_anim.pos)
    return [Sprite(
      image=(type(banner_anim) is PauseAnim and banner.image_written or banner.image),
      pos=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3),
      size=(banner.image.get_width(), banner_height),
      origin=("center", "center"),
      layer="ui"
    )]
