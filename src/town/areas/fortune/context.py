from contexts.shop import ShopContext, ShopCard
from cores.mira import MiraCore as Oracle
from portraits.mira import MiraPortrait as OraclePortrait
from palette import BLUE_DARK

class FortuneContext(ShopContext):
  def __init__(ctx, *args, **kwargs):
    super().__init__(
      title="Fortune House",
      subtitle="Destiny written in starlight",
      messages={
        "home": Oracle.name.upper() + ": What can I do you for...?",
        "home_again": Oracle.name.upper() + ": Anything else...?",
        "sell": {
          "home": Oracle.name.upper() + ": Got something to sell me?",
          "thanks": Oracle.name.upper() + ": Thanks!"
        },
        "exit": Oracle.name.upper() + ": Come again..."
      },
      bg_name="fortune_bg",
      bg_color=BLUE_DARK,
      portraits=[OraclePortrait()],
      cards=[
        ShopCard(name="buy", text="Buy recovery and support items."),
        ShopCard(name="sell", text="Trade in items for gold."),
        ShopCard(name="exit", text="Leave the shop.")
      ],
      *args,
      **kwargs
    )
