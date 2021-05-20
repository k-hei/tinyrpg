from contexts.app import App
from contexts.prompt import PromptContext, Choice

App(title="prompt demo",
  context=PromptContext("Are you sure you want to quit?", (
    Choice(text="Yes"),
    Choice(text="No", default=True, closing=True)
  ), on_choose=lambda choice: (
    choice.text == "Yes" and True
    or choice.text == "No" and False
  ))
).init()
