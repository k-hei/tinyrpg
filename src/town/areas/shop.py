from town.topview.stage import Stage, Link
from town.topview.actor import Actor
from contexts.prompt import PromptContext, Choice
from cores.knight import KnightCore
from cores.rogue import RogueCore
from palette import ORANGE, GREEN

class ShopArea(Stage):
  bg_id = "shop"
  links = {
    "entrance": Link(cell=(2, 6), direction=(0, 1)),
    "backdoor": Link(cell=(3, 0), direction=(0, -1))
  }
  layout = [
    "###+####",
    "#.#.2..#",
    "#.####.#",
    "#.''''.#",
    "#......#",
    "#.0...1#",
    "##+#####",
  ]
  actors = {
    "0": "hero",
    "1": Actor(
      core=RogueCore(),
      cell=(6, 5),
      facing=(1, 0),
      color=GREEN,
      moving=True,
      message=lambda talkee, ctx: [
        (talkee.get_name(), "You know what I can't get enough of?"),
        (talkee.get_name(), "BBWs."),
        (talkee.get_name(), "Big beautiful wings.....")
      ]
    ),
    "2": Actor(
      core=KnightCore(name="Arthur"),
      cell=(4, 1),
      facing=(0, 1),
      color=ORANGE,
      moving=True,
      move_period=45,
      is_shopkeep=True,
      message=lambda talkee, ctx: (
        ctx.hero.get_rect().centery > talkee.get_rect().centery and [
          shop := PromptContext(
            message="{}: How can I help you?".format(talkee.get_name().upper()),
            choices=[
              Choice("Buy items"),
              Choice("Sell items"),
              Choice("Nothing", closing=True)
            ],
            required=True,
            on_close=lambda choice: (
              choice and choice.text == "Buy items" and [
                "This feature isn't implemented yet...",
                shop
              ] or choice and choice.text == "Sell items" and [
                "This feature isn't implemented yet...",
                shop
              ]
            )
          ),
        ] or [
          (talkee.get_name(), "Aha nooo, we can'tttt"),
          (talkee.get_name(), "Not during business hours...")
        ]
      )
    )
  }
