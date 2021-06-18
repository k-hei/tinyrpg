from contexts.app import App
from contexts.shop import ShopContext
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
    bg_image="store_bg",
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
