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
from transits.dissolve import DissolveOut
from savedata.resolve import resolve_item
from colors.palette import ORANGE, WHITE, CORAL

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
    open_shop = lambda ctx: [
      lambda: StoreContext(hud=ctx.hud, store=ctx.store),
      lambda: ctx.anims.append(ctx.HudAnim()),
      lambda: ctx.get_head().transition([DissolveOut()])
    ]
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
          "{}: Ever get a rebar stuck up your ass?".format(talkee.name.upper()),
          *open_shop(ctx)
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
          "{}: Welcome!".format(talkee.name.upper()),
          *open_shop(ctx)
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
          (talkee.name, "You know what I can't get enough of?"),
          (talkee.name, "BBWs."),
          (talkee.name, "Big beautiful wings..."),
        ]
      ),
      "Y": Planter,
      "P": PotionStock,
      "B": BreadStock,
      "C": CheeseStock,
      "-": Counter,
      "+": lambda: Door(palette=(CORAL, WHITE))
    })
