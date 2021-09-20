from dungeon.props import Prop
import assets
from anims.flicker import FlickerAnim
from sprite import Sprite
from filters import replace_color
from config import FLICKER_DURATION
from colors.palette import WHITE, GOLD

class Palm(Prop):
  solid = False

  def vanish(palm, game):
    game.anims.append([FlickerAnim(
      duration=FLICKER_DURATION,
      target=palm,
      on_end=lambda: game.floor.elems.remove(palm)
    )])

  def view(coffin, anims):
    palm_image = assets.sprites["oasis_palm"]
    palm_image = replace_color(palm_image, WHITE, GOLD)
    return super().view([Sprite(
      image=palm_image,
      layer="elems",
      offset=-16
    )], anims)
