from town.topview.stage import Stage, Link
from town.topview.actor import Actor
from town.topview.door import Door
from town.areas.fortune.stand import FortuneStand
from town.areas.fortune.desk import FortuneDesk
from town.areas.fortune.context import FortuneContext
from cores.mira import MiraCore
from transits.dissolve import DissolveOut
from colors.palette import BLACK, ORANGE, DARKBLUE

class FortuneArea(Stage):
  name = "Fortune House"
  bg = "fortune"
  dark = True
  scale = 16
  ports = {
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
          "{}: Welcome...".format(talkee.name.upper()),
          lambda: FortuneContext(hud=ctx.hud, store=ctx.store),
          lambda: ctx.anims.append(ctx.HudAnim()),
          lambda: ctx.get_head().transition([DissolveOut()])
        ]
      ),
      "2": FortuneDesk,
      "|": FortuneStand,
      "+": lambda: Door(palette=(BLACK, DARKBLUE))
    })
