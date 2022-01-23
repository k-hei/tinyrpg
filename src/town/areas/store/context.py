from contexts.shop import ShopContext, ShopCard
from cores.husband import Husband as Husband
from cores.wife import Wife as Wife
from portraits.husband import HusbandPortrait
from portraits.wife import WifePortrait

class StoreContext(ShopContext):
  def __init__(ctx, *args, **kwargs):
    super().__init__(
      title="Market",
      subtitle="All your exploration needs",
      messages={
        "home": Husband.name.upper() + ": HOW CAN I HELP YOU?",
        "home_again": Husband.name.upper() + ": WILL THAT BE ALL FOR TODAY?",
        "sell": {
          "home": Wife.name.upper() + ": Got something to sell me?",
          "home_again": Wife.name.upper() + ": Anything else to sell?",
          "confirm": Wife.name.upper() + ": That'll be {gold}G. OK?",
          "thanks": Wife.name.upper() + ": Thanks!"
        },
        "exit": Wife.name.upper() + ": See you soon!"
      },
      bg_name="buy_bgtile",
      portraits=[HusbandPortrait(), WifePortrait()],
      cards=[
        ShopCard(name="buy", text="Buy recovery and support items.", portrait=HusbandPortrait),
        ShopCard(name="sell", text="Trade in items for gold.", portrait=WifePortrait),
        ShopCard(name="exit", text="Leave the shop.")
      ],
      *args,
      **kwargs
    )
