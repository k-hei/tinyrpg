from contexts import Context
from contexts.app import App
from contexts.prompt import PromptContext, Choice
from comps.hud import Hud
from cores.knight import Knight
from cores.mage import Mage

class HudContext(Context):
  def __init__(ctx):
    super().__init__()
    ctx.party = [Knight()]
    ctx.hud = Hud(party=ctx.party, hp=True)
    ctx.open(PromptContext(
      message="Select an action to perform.",
      choices=[
        Choice(text="+5 HP"),
        Choice(text="-5 HP"),
        Choice(text="Toggle ally"),
        Choice(text="Switch char", disabled=lambda: len(ctx.party) == 1),
      ],
      required=True,
      on_choose=lambda choice: (
        choice.text == "+5 HP" and ctx.heal_char()
        or choice.text == "-5 HP" and ctx.damage_char()
        or choice.text == "Toggle ally" and ctx.toggle_char()
        or choice.text == "Switch char" and ctx.switch_char()
      ) and False
    ))

  def heal_char(ctx):
    hero = ctx.party[0]
    if hero.dead:
      hero.revive(hp_factor=0)
    else:
      hero.heal(hp=5)

  def damage_char(ctx):
    hero = ctx.party[0]
    hero.damage(hp=5)

  def toggle_char(ctx):
    if len(ctx.party) > 1:
      ctx.party.pop()
    else:
      ctx.party.append((Mage if type(ctx.party[0]) is Knight else Knight)())

  def switch_char(ctx):
    if len(ctx.party) == 1:
      return False
    ctx.party.reverse()
    return True

  def update(ctx):
    ctx.hud.update()

  def view(ctx):
    return ctx.hud.view() + super().view()

App(
  title="hud demo",
  context=HudContext()
).init()
