from contexts.data import DataContext
from contexts.dialogue import DialogueContext
from contexts.prompt import PromptContext, Choice
import savedata

class SaveContext(DataContext):
  title = "SAVE DATA"
  action = "Save"

  def __init__(ctx, data, on_close=None):
    super().__init__(on_close=on_close)
    ctx.data = data

  def enter(ctx):
    super().enter()
    ctx.anims[-1].on_end = lambda: ctx.open(
      DialogueContext(script=["Please select a slot to save to."], lite=True)
    )

  def handle_action(ctx):
    slot = ctx.slots[ctx.index]
    old_data = slot.data
    new_data = ctx.data
    def save():
      savedata.save("src/data{}.json".format(ctx.index), new_data.__dict__)
      slot.save(new_data)
      ctx.open(DialogueContext(
        script=[
          "Data saved successfully.",
          lambda: PromptContext("Return to the game?", [
            Choice("Yes"),
            Choice("No", closing=True)
          ], on_close=lambda choice: (
            choice and choice.text == "Yes" and ctx.exit()
          ))
        ],
        lite=True
      ))
    if old_data is None:
      save()
    else:
      ctx.open(PromptContext("Overwrite this file?", [
        Choice("Yes"),
        Choice("No", default=True, closing=True)
      ], on_close=lambda choice: (
        choice and choice.text == "Yes" and save()
      )))
