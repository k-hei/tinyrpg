from contexts.app import App
from contexts.prompt import PromptContext, Choice

App(
  title="prompt demo",
  context=PromptContext("Are you sure you want to quit?", (
    Choice(
      text="Yes",
      on_choose=lambda close: (print("yes"), close())
    ),
    Choice(
      text="No",
      on_choose=lambda _: print("no"),
      default=True
    )
  ))
).init()
