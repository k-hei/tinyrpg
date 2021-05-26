from town.actors.npc import Npc
from contexts.prompt import PromptContext, Choice
from cores.knight import KnightCore

class Knight(Npc):
  def __init__(knight, core=KnightCore()):
    super().__init__(core=core, messages=[
      lambda town: [
        PromptContext((knight.get_name().upper(), ": ", "I HATE THE PHARAOH! I HATE THE PHARAOH!"), (
          Choice("\"Let's go!\""),
          Choice("\"Maybe later...\"")
        ), required=True, on_close=lambda choice: (
          choice.text == "\"Let's go!\"" and [
            lambda: town.recruit(town.talkee)
          ] or choice.text == "\"Maybe later...\"" and []
        ))
      ]
    ])
    knight.core.faction = "player"
    knight.y = 0

  def render(knight):
    return knight.core.render()
