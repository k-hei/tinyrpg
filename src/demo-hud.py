from contexts import Context
from contexts.app import App
from contexts.prompt import PromptContext, Choice
from comps.hud import Hud
from cores.knight import Knight
from sprite import Sprite

class HudContext(Context):
  def __init__(ctx):
    super().__init__()
    ctx.party = [Knight()]
    ctx.hud = Hud(party=ctx.party, hp=True)

  def init(ctx):
    ctx.open(PromptContext(
      message="Select an action to perform.",
      choices=[
        Choice(text="+5 HP"),
        Choice(text="-5 HP"),
        Choice(text="Toggle char"),
      ],
      required=True,
      on_choose=lambda choice: (
        choice.text == "+5 HP" and (
          ctx.party[0].revive(hp_factor=0)
          or ctx.party[0].heal(hp=5)
        ) or choice.text == "-5 HP" and (
          ctx.party[0].damage(hp=5)
        )
      ) and False
    ))

  def update(ctx):
    super().update()
    ctx.hud.update()

  def view(ctx):
    return ctx.hud.view() + super().view()

App(
  title="hud demo",
  context=HudContext()
).init()
