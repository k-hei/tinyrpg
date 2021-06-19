from contexts.app import App
from contexts.shop import ShopContext, ShopCard
from savedata.resolve import resolve_item
from portraits.husband import HusbandPortrait
from portraits.wife import WifePortrait
from palette import WHITE

App(
  title="shop demo",
  context=ShopContext(
    title="General Store",
    subtitle="All your exploration needs",
    messages=["THAG: How can I help you?", "THAG: Anything else?"],
    bg="store_bg",
    cards=[
      ShopCard(name="buy", text="Buy recovery and support items.", portrait=HusbandPortrait),
      ShopCard(name="sell", text="Trade in items for gold.", portrait=WifePortrait),
      ShopCard(name="exit", text="Leave the shop.")
    ],
    portraits=[HusbandPortrait(), WifePortrait()],
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
