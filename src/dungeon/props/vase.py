import assets
from sprite import Sprite
from dungeon.props import Prop
from colors.palette import WHITE, DARKBLUE
from filters import replace_color
from anims.frame import FrameAnim

class Vase(Prop):
  active = True

  class OpenAnim(FrameAnim):
    frames = assets.sprites["vase_opening"]
    frames_duration = 5

  def __init__(vase, contents=None, opened=False, *args, **kwargs):
    super().__init__(vase, *args, **kwargs)
    vase.contents = contents
    vase.opened = opened
    vase.anim = None

  def open(vase, game):
    if vase.opened:
      return False
    vase.opened = True
    game.anims[0].append(Vase.OpenAnim(target=vase))
    return True

  def effect(vase, game):
    if game.obtain(vase.contents, target=vase):
      vase.open(game)

  def view(vase, anims=[], *args, **kwargs):
    anim_group = [a for a in anims[0] if a.target is vase] if anims else []
    for anim in anim_group:
      if isinstance(anim, FrameAnim):
        vase_image = anim.frame()
        break
    else:
      if vase.opened:
        vase_image = assets.sprites["vase_opened"]
      else:
        vase_image = assets.sprites["vase"]
    vase_image = replace_color(vase_image, (0xFF, 0x00, 0x00), DARKBLUE)
    return super().view([Sprite(
      image=vase_image
    )], anims, *args, **kwargs)
