from contexts.app import App
from contexts.sell import SellContext
from savedata.resolve import resolve_item
from portraits.mira import MiraPortrait as OraclePortrait
from cores.mira import MiraCore as Oracle

ORACLE_NAME = Oracle.name.upper()
App(
  title="shop sell demo",
  context=SellContext(
    portrait=OraclePortrait(),
    messages={
      "home": "{}: Got something to sell me?".format(ORACLE_NAME),
      "thanks": "{}: Thanks!".format(ORACLE_NAME)
    },
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
).init()
