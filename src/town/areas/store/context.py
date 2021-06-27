from contexts.shop import ShopContext, ShopCard
from cores.husband import Husband as Husband
from cores.wife import Wife as Wife
from portraits.husband import HusbandPortrait
from portraits.wife import WifePortrait

class StoreContext(ShopContext):
  def __init__(ctx, *args, **kwargs):
    super().__init__(
      title="General Store",
      subtitle="All your exploration needs",
      messages={
        "home": Husband.name.upper() + ": How can I help you?",
        "home_again": Husband.name.upper() + ": Will that be all for today?",
        "sell": {
          "home": Wife.name.upper() + ": Got something to sell me?",
          "thanks": Wife.name.upper() + ": Thanks!"
        },
        "exit": Wife.name.upper() + ": See you soon!"
      },
      bg_name="store_bg",
      portraits=[HusbandPortrait(), WifePortrait()],
      cards=[
        ShopCard(name="buy", text="Buy recovery and support items.", portrait=HusbandPortrait),
        ShopCard(name="sell", text="Trade in items for gold.", portrait=WifePortrait),
        ShopCard(name="exit", text="Leave the shop.")
      ],
      *args,
      **kwargs
    )
