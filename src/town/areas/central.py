from town.sideview.stage import Area, AreaLink
from town.sideview.actor import Actor
from cores.mage import Mage

from assets import load as use_assets
from config import TILE_SIZE, WINDOW_WIDTH
from sprite import Sprite

from contexts.prompt import PromptContext, Choice
from contexts.nameentry import NameEntryContext
from contexts.load import LoadContext
from contexts.save import SaveContext

class CentralArea(Area):
  name = "Town Square"
  bg = "town_central"
  links = {
    "right": AreaLink(x=416, direction=(1, 0)),
    "alley": AreaLink(x=272, direction=(0, -1)),
    "door_triangle": AreaLink(x=64, direction=(0, -1)),
    "door_heart": AreaLink(x=192, direction=(0, -1)),
  }

  def init(area, ctx):
    super().init(ctx)
    if not next((a for a in ctx.party if type(a.core) is Mage), None):
      area.spawn(Actor(core=Mage(
        faction="ally",
        facing=(1, 0)
      )), (112, 0))
