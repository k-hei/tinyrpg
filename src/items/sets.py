from items.ailment.amethyst import Amethyst
from items.ailment.antidote import Antidote
from items.ailment.booze import Booze
from items.ailment.lovepotion import LovePotion
from items.ailment.musicbox import MusicBox
from items.ailment.topaz import Topaz
from items.dungeon.balloon import Balloon
from items.dungeon.emerald import Emerald
from items.hp.ankh import Ankh
from items.hp.elixir import Elixir
from items.hp.potion import Potion
from items.hp.ruby import Ruby
from items.sp.berry import Berry
from items.sp.bread import Bread
from items.sp.cheese import Cheese
from items.sp.fish import Fish
from items.sp.sapphire import Sapphire

T1_ITEMS = [Cheese, Bread, Antidote]
T2_ITEMS = [Potion, Fish, MusicBox, LovePotion, Booze]
T3_ITEMS = [Elixir, Ankh, Ruby, Sapphire, Emerald, Amethyst, Topaz, Berry]

NORMAL_ITEMS = (
  T1_ITEMS * 2
  + T2_ITEMS
)

SPECIAL_ITEMS = (
  T1_ITEMS * 5
  + T2_ITEMS * 3
  + T3_ITEMS
)
