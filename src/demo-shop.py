from contexts.app import App
from town.areas.store.context import StoreContext
from game.store import GameStore
from savedata.resolve import resolve_item
from cores.knight import Knight
from cores.mage import Mage

App(
  title="shop demo",
  context=StoreContext(
    store=GameStore(
      party=[Knight(), Mage()],
      items=[resolve_item(i) for i in [
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
      ]],
    )
  )
).init()
