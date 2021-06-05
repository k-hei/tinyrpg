from contexts.app import App
from contexts.shop import ShopContext
from savedata.resolve import resolve_item

App(
  title="shop demo",
  context=ShopContext(
    items=list(map(resolve_item, [
      "Potion",
      "Potion",
      "Ankh",
      "Elixir",
      "Cheese",
      "Cheese",
      "Cheese",
      "Bread",
      "Fish",
      "Fish",
      "Balloon",
      "Emerald",
      "Antidote",
      "Antidote",
      "Antidote",
      "Antidote",
      "Amethyst",
      "AngelTears",
      "AngelTears",
      "RedFerrule",
      "Diamond"
    ]))
  )
).init()
