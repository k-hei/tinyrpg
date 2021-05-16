from contexts.app import App
from contexts.prompt import PromptContext, Choice

App(title="prompt demo",
  context=PromptContext("Are you sure you want to quit?", (
    Choice(text="Yes"),
    Choice(text="No", default=True)
  ), on_choose=lambda choice, close: (
    choice.text == "Yes" and (print("yes"), close())
    or choice.text == "No" and print("no")
  ))
).init()
