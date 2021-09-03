from comps import Component
from anims.tween import TweenAnim
from anims.pause import PauseAnim
from sprite import Sprite
from filters import replace_color
import assets
from config import WINDOW_WIDTH, WINDOW_HEIGHT

BANNER_COLOR = (255, 0, 0)

class EnterAnim(TweenAnim): pass
class ExitAnim(TweenAnim): pass

class SkillBanner(Component):
  def __init__(banner, text, color, *args, **kwargs):
    super().__init__(*args, **kwargs)
    banner.anims = [
      EnterAnim(duration=15),
      PauseAnim(duration=90),
      ExitAnim(duration=8),
    ]
    banner.image = replace_color(assets.sprites["skill_banner"], BANNER_COLOR, color)
    banner.image_written = banner.image.copy()
    Sprite(
      image=assets.ttf["normal"].render(text),
      pos=(banner.image.get_width() // 2, banner.image.get_height() // 2),
      origin=("center", "center"),
    ).draw(banner.image_written)

  def update(banner):
    if banner.done:
      return
    anim = banner.anims and banner.anims[0]
    if anim.done:
      banner.anims.remove(anim)
    else:
      anim.update()
    if not banner.anims:
      banner.done = True

  def view(banner):
    banner.update()
    if banner.done:
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
      pos=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4),
      size=(banner.image.get_width(), banner_height),
      origin=("center", "center"),
      layer="ui"
    )]
