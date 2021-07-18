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
        "home": "{}: What can I do you for...?".format(ORACLE_NAME),
        "home_again": "{}: Anything else...?".format(ORACLE_NAME),
        "sell": {
          "home": "{}: Got something to sell me?".format(ORACLE_NAME),
          "thanks": "{}: Thanks!".format(ORACLE_NAME)
        },
        "exit": "{}: Come again...".format(ORACLE_NAME)
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
