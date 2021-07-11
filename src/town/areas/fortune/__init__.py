from town.topview.stage import Stage, Link
from town.topview.actor import Actor
from town.topview.door import Door
from town.areas.fortune.stand import FortuneStand
from town.areas.fortune.desk import FortuneDesk
from town.areas.fortune.context import FortuneContext
from contexts.prompt import PromptContext, Choice
from contexts.shop import ShopContext
from cores.mira import MiraCore
from cores.rogue import Rogue
from transits.dissolve import DissolveOut
from savedata.resolve import resolve_item
from palette import BLACK, ORANGE, BLUE_DARK

class FortuneArea(Stage):
  name = "Fortune House"
  bg = "fortune"
  dark = True
  scale = 16
  links = {
    "entrance": Link(cell=(2, 6), direction=(0, 1))
  }
  layout = [
    "################",
    "################",
    "################",
    "################",
    "###..........###",
    "###....1.....###",
    "###..........###",
    "###...2####..###",
    "###..........###",
    "##............##",
    "##.....0......##",
    "##....|..|....##",
    "#######+.#######",
    "#######..#######",
  ]

  def __init__(stage, hero):
    super().__init__(stage.layout, {
      "0": hero,
      "1": Actor(
        core=MiraCore(),
        facing=(0, 1),
        color=ORANGE,
        moving=True,
        move_period=45,
        is_shopkeep=True,
        message=lambda talkee, ctx: [
          "{}: Welcome...".format(talkee.get_name().upper()),
          lambda: FortuneContext(hud=ctx.hud, items=ctx.get_inventory().items),
          lambda: ctx.anims.append(ctx.HudAnim()),
          lambda: ctx.get_head().transition(DissolveOut())
        ]
      ),
      "2": FortuneDesk,
      "|": FortuneStand,
      "+": lambda: Door(palette=(BLACK, BLUE_DARK))
    })
