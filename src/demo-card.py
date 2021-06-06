from contexts.app import App
from contexts.cardgroup import CardContext

App(
  title="card demo",
  size=(100, 52),
  context=CardContext()
).init()
