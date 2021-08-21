from contexts.app import App
from town.areas.store.context import StoreContext
from game.data import GameData
from savedata.resolve import resolve_item

App(
  title="shop demo",
  context=StoreContext(
    store=GameData(items=[resolve_item(i) for i in [
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
    ]])
  )
).init()
