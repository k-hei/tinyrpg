from town.actors.npc import Npc
from contexts.prompt import PromptContext, Choice
from cores.mage import MageCore

class Mage(Npc):
  def __init__(mage, core=MageCore()):
    super().__init__(core=core, messages=[
      lambda town: [
        PromptContext((mage.get_name().upper(), ": ", "Are you ready yet?"), (
          Choice("\"Let's go!\""),
          Choice("\"Maybe later...\"")
        ), required=True, on_close=lambda choice: (
          choice.text == "\"Let's go!\"" and (
            (town.hero.get_name(), "Let's get going!"),
            (mage.get_name(), "Jeez, about time..."),
            lambda: town.recruit(town.talkee)
          ) or choice.text == "\"Maybe later...\"" and (
            (town.hero.get_name(), "Give me a second..."),
            (mage.get_name(), "You know I don't have all day, right?")
          )
        ))
      ]
    ])

  def render(mage):
    return mage.core.render()
