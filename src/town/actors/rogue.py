from town.actors.npc import Npc
from contexts.prompt import PromptContext, Choice
from cores.rogue import Rogue
from anims.walk import WalkAnim
import pygame

class Rogue(Npc):
  def __init__(rogue, core=Rogue()):
    super().__init__(core=core, messages=[
      lambda town: [
        (rogue.get_name(), "Yeah, baby!"),
        PromptContext(("I'm gettin' hard!\nSo hard for you, baby!"), (
          Choice("\"So true\""),
          Choice("\"What?\"")
        ), required=True, on_close=lambda choice: (
          choice.text == "\"So true\"" and (
            (town.hero.core.name, "So true, bestie"),
            (rogue.get_name(), "Oh baby, yes!"),
            (rogue.get_name(), "Let's dance 'til the break of dawn!"),
            lambda: town.recruit(town.talkee)
          ) or choice.text == "\"What?\"" and (
            (town.hero.core.name, "What the hell are you talking about?"),
            (town.ally
              and (town.ally.core.name, "Let's just leave him be...")
              or (rogue.get_name(), "You're no fun, you know that?"))
          )
        ))
      ]
    ])

  def update(rogue):
    super().update()
    if not rogue.anim and rogue.core.faction == "ally":
      rogue.anim = WalkAnim(period=30)
      rogue.core.anims.append(rogue.anim)

  def render(rogue):
    return rogue.core.render()
