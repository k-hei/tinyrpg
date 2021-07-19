from contexts.shop import ShopContext, ShopCard
from cores.mira import MiraCore as Oracle
from portraits.mira import MiraPortrait as OraclePortrait
from colors.palette import DARKBLUE

class FortuneContext(ShopContext):
  def __init__(ctx, *args, **kwargs):
    ORACLE_NAME = Oracle.name.upper()
    super().__init__(
      title="Fortune House",
      subtitle="Destiny written in starlight",
      messages={
        "home": ORACLE_NAME + ": What can I do you for...?",
        "home_again": ORACLE_NAME + ": Anything else...?",
        "sell": {
          "home": ORACLE_NAME + ": Got something to sell me?",
          "home_again": ORACLE_NAME + ": Anything else to sell?",
          "confirm": ORACLE_NAME + ": That'll be {gold}G. OK?",
          "thanks": ORACLE_NAME + ": Thanks!"
        },
        "exit": ORACLE_NAME + ": Come again..."
      },
      bg_name="fortune_bg",
      bg_color=DARKBLUE,
      portraits=[OraclePortrait()],
      cards=[
        ShopCard(name="buy", text="Buy recovery and support items."),
        ShopCard(name="sell", text="Trade in items for gold."),
        ShopCard(name="exit", text="Leave the shop.")
      ],
      *args,
      **kwargs
    )
