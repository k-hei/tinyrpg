from contexts.data import DataContext
from contexts.dialogue import DialogueContext
from contexts.prompt import PromptContext, Choice
from transits.dissolve import DissolveIn, DissolveOut
from game.data import GameData

class LoadContext(DataContext):
  title = "LOAD DATA"
  action = "Load"

  def enter(ctx):
    super().enter()
    ctx.anims[-1].on_end = lambda: ctx.open(
      DialogueContext(script=["Please select a file to load."], lite=True)
    )

  def handle_action(ctx):
    savedata = ctx.slots[ctx.index].data
    if savedata is None:
      return False
    gamedata = GameData.decode(savedata)
    ctx.open(PromptContext("Load this file?", [
      Choice("Yes"),
      Choice("No", closing=True)
    ], on_close=lambda choice:
      choice.text == "Yes" and ctx.open(DialogueContext(
        script=["Save data loaded successfully."],
        lite=True,
        on_close=lambda: ctx.get_head().transition([
          DissolveIn(on_end=lambda: ctx.close(gamedata)),
          DissolveOut()
        ])
      ))
    ))
