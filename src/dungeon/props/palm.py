from dungeon.props import Prop
from anims.flicker import FlickerAnim
from config import FLICKER_DURATION
from assets import load as use_assets
from sprite import Sprite

class Palm(Prop):
  def __init__(palm):
    super().__init__(solid=False)

  def vanish(palm, game):
    game.anims.append([FlickerAnim(
      duration=FLICKER_DURATION,
      target=palm,
      on_end=lambda: game.floor.elems.remove(palm)
    )])

  def view(coffin, anims):
    return super().view(Sprite(
      image=use_assets().sprites["oasis_palm"],
      layer="elems",
      offset=-16
    ), anims)
