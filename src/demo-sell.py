from contexts.app import App
from contexts.sell import SellContext
from savedata.resolve import resolve_item

App(
  title="shop sell demo",
  context=SellContext(
    items=list(map(resolve_item, ["Potion", "Potion", "Fish", "Emerald", "Antidote", "AngelTears", "ToxicFerrule"]))
  )
).init()
