from dataclasses import dataclass
from items.sp import SpItem

@dataclass
class Sapphire(SpItem):
  name: str = "Sapphire"
  desc: str = "Restores\nfull SP."
  sprite: str = "gem"
  value: int = 100
  rarity: int = 3

  def use(elixir, store):
    if type(store.place).__name__.startswith("Town"):
      return False, "You can't use that here!"
    if store.sp < store.sp_max:
      store.sp = store.sp_max
      return True, "The party restored full SP."
    else:
      return False, "Nothing to restore!"
