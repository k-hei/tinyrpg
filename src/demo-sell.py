from contexts.app import App
from contexts.sell import SellContext
from resolve.item import resolve_item
from portraits.mira import MiraPortrait as OraclePortrait
from cores.mira import MiraCore as Oracle
from game.store import GameStore

ORACLE_NAME = Oracle.name.upper()
App(
  title="shop sell demo",
  context=SellContext(
    portrait=OraclePortrait(),
    messages={
      "home": Oracle.name.upper() + ": Got something to sell me?",
      "home_again": Oracle.name.upper() + ": Anything else to sell?",
      "confirm": Oracle.name.upper() + ": That'll be {gold}G. OK?",
      "thanks": Oracle.name.upper() + ": Thanks!"
    },
    store=GameStore(
      gold=500,
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
      ]]
    )
  )
).init()
