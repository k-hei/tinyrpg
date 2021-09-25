from dungeon.element import DungeonElement
import assets
from filters import replace_color
from colors.palette import WHITE, BLACK, GOLD, VIOLET
from sprite import Sprite
from anims.frame import FrameAnim

class Altar(DungeonElement):
  solid = True
  static = True
  active = True

  def __init__(altar, on_action=None, *args, **kwargs):
    super().__init__(static=True, *args, **kwargs)
    altar.on_action = on_action
    altar.opened = False

  def effect(altar, game):
    if altar.opened:
      return False
    altar.opened = True
    altar.on_action and altar.on_action(game.room, game)
    return False

  def view(altar, anims):
    altar_image = assets.sprites["altar"]
    if altar.opened:
      altar_image = assets.sprites["altar_open"]
    altar_image = replace_color(altar_image, WHITE, GOLD)
    altar_sprite = Sprite(
      image=replace_color(altar_image, WHITE, GOLD),
      layer="elems"
    )
    return super().view([altar_sprite], anims)
