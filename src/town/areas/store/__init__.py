from town.topview.stage import Stage, Link
from town.topview.actor import Actor
from town.topview.door import Door
from town.areas.store.planter import Planter
from town.areas.store.potionstock import PotionStock
from town.areas.store.breadstock import BreadStock
from town.areas.store.cheesestock import CheeseStock
from town.areas.store.counter import Counter
from town.areas.store.context import StoreContext
from contexts.prompt import PromptContext, Choice
from contexts.shop import ShopContext, ShopCard
from cores.husband import Husband
from cores.wife import Wife
from cores.rogue import Rogue
from portraits.husband import HusbandPortrait
from portraits.wife import WifePortrait
from savedata.resolve import resolve_item
from palette import ORANGE, WHITE

class StoreArea(Stage):
  name = "General Store"
  bg = "store_tiles"
  fg = "store_fg"
  scale = 16
  links = {
    "entrance": Link(cell=(2, 6), direction=(0, 1))
  }
  layout = [
    "################",
    "################",
    "################",
    "#..##..####...##",
    "#Y....##.1.2..##",
    "#.....##......##",
    "#.....#######-##",
    "#Y..C####.....##",
    "#.............##",
    "#.............##",
    "#Y..B#.0..P#..##",
    "#3............##",
    "#######+.#######",
    "#######..#######",
  ]

  def __init__(stage, party):
    shop = lambda: StoreContext(items=[])
    super().__init__(stage.layout, {
      "0": party,
      "1": Actor(
        core=Husband(),
        facing=(0, 1),
        color=ORANGE,
        moving=True,
        move_period=45,
        is_shopkeep=True,
        message=lambda talkee, ctx: [
          "{}: Ever get a rebar stuck up your ass?".format(talkee.get_name().upper()),
          shop,
          lambda: ctx.anims.append(ctx.HudAnim()),
          lambda: ctx.get_root().dissolve_out()
        ]
      ),
      "2": Actor(
        core=Wife(),
        facing=(0, 1),
        color=ORANGE,
        moving=True,
        move_period=40,
        is_shopkeep=True,
        message=lambda talkee, ctx: [
          "{}: Welcome!".format(talkee.get_name().upper()),
          shop,
          lambda: ctx.anims.append(ctx.HudAnim()),
          lambda: ctx.get_root().dissolve_out()
        ]
      ),
      "3": Actor(
        core=Rogue(faction="ally"),
        facing=(-1, 0),
        moving=True,
        move_period=30,
        is_shopkeep=True,
        spawn_offset=(0, -8),
        message=lambda talkee, ctx: [
          (talkee.get_name(), "You know what I can't get enough of?"),
          (talkee.get_name(), "BBWs."),
          (talkee.get_name(), "Big beautiful wings..."),
        ]
      ),
      "Y": Planter,
      "P": PotionStock,
      "B": BreadStock,
      "C": CheeseStock,
      "-": Counter,
      "+": lambda: Door(palette=(0xFFE6A8A8, WHITE))
    })
