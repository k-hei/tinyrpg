from dungeon.props import Prop
from anims.flicker import FlickerAnim
from config import FLICKER_DURATION
from assets import load as use_assets

class Palm(Prop):
  def __init__(palm):
    super().__init__(solid=False)

  def vanish(palm, game):
    game.anims.append([FlickerAnim(
      duration=FLICKER_DURATION,
      target=palm,
      on_end=lambda: game.floor.elems.remove(palm)
    )])

  def render(coffin, anims):
    return use_assets().sprites["oasis_palm"]