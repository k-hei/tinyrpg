from contexts.app import App
from contexts.sell import SellContext

App(
  title="shop sell demo",
  context=SellContext(
    items=[]
  )
).init()
