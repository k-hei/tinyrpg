from town.topview.stage import Stage, Link
from town.topview.actor import Actor
from town.topview.door import Door
from town.areas.store.planter import Planter
from town.areas.store.potionstock import PotionStock
from town.areas.store.breadstock import BreadStock
from town.areas.store.cheesestock import CheeseStock
from town.areas.store.counter import Counter
from contexts.prompt import PromptContext, Choice
from contexts.shop import ShopContext, ShopCard
from cores.husband import HusbandCore
from cores.wife import WifeCore
from portraits.husband import HusbandPortrait
from portraits.wife import WifePortrait
from savedata.resolve import resolve_item
from palette import ORANGE, WHITE

class StoreArea(Stage):
  bg_id = "store_tiles"
  fg_id = "store_fg"
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
    "#.............##",
    "#######+.#######",
    "#######..#######",
  ]

  def __init__(stage, hero):
    shop = lambda: ShopContext(
      title="General Store",
      subtitle="All your exploration needs",
      messages={
        "home": "THAG: How can I help you?",
        "home_again": "THAG: Will that be all for today?",
        "sell": {
          "home": "SYLVIA: Got something to sell me?",
          "thanks": "SYLVIA: Thanks!"
        },
        "exit": "SYLVIA: See you soon!"
      },
      bg="store_bg",
      portraits=[HusbandPortrait(), WifePortrait()],
      cards=[
        ShopCard(name="buy", text="Buy recovery and support items.", portrait=HusbandPortrait),
        ShopCard(name="sell", text="Trade in items for gold.", portrait=WifePortrait),
        ShopCard(name="exit", text="Leave the shop.")
      ],
      items=list(map(resolve_item, [
        "Potion",
        "Potion",
        "Ankh",
        "Elixir",
        "Cheese",
        "Cheese",
        "Cheese",
        "Bread",
        "Fish",
        "Fish",
        "Balloon",
        "Emerald",
        "Antidote",
        "Antidote",
        "Antidote",
        "Antidote",
        "Amethyst",
        "AngelTears",
        "AngelTears",
        "RedFerrule",
        "Diamond"
      ]))
    )
    super().__init__(stage.layout, {
      "0": hero,
      "1": Actor(
        core=HusbandCore(),
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
        core=WifeCore(),
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
      "Y": Planter,
      "P": PotionStock,
      "B": BreadStock,
      "C": CheeseStock,
      "-": Counter,
      "+": lambda: Door(palette=(0xFFE6A8A8, WHITE))
    })
