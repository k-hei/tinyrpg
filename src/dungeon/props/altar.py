from dungeon.element import DungeonElement
from assets import load as use_assets
from filters import replace_color
from colors.palette import WHITE, BLACK, GOLD, VIOLET
from sprite import Sprite
from anims.frame import FrameAnim

class Altar(DungeonElement):
  def __init__(altar, *args, **kwargs):
    super().__init__(*args, **kwargs)
    altar.reset_anim()

  def reset_anim(altar):
    altar.anim = FrameAnim(
      frames=["fx_soul{}".format(i) for i in range(6)],
      duration=60
    )

  def update(altar):
    altar.anim.update()
    if altar.anim.done:
      altar.reset_anim()

  def view(altar, anims):
    assets = use_assets()
    sprites = [Sprite(
      image=replace_color(assets.sprites["altar"], WHITE, GOLD),
      layer="elems"
    )]
    if altar.anim.time % 2:
      sprites.append(Sprite(
        image=replace_color(assets.sprites[altar.anim.frame], BLACK, VIOLET),
        pos=(0, -24),
        origin=("center", "center"),
        layer="numbers"
      ))
    return super().view(sprites, anims)
