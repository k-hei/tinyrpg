from random import randint
from lib.graph import Graph
import assets
from dungeon.floors import Floor
from dungeon.room import Blob as Room
from dungeon.gen import gen_floor
from dungeon.gen.blob import gen_blob
from dungeon.roomdata import rooms

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

class GenericFloor(Floor):
  def generate(store=None, seed=None):
    return gen_floor(
      features=[
        Room(data=rooms["entry"]),
        Room(data=rooms["exit"]),
        *([Room(data=rooms["oasis"])] if randint(1, 3) == 1 else []),
      ],
      extra_room_count=4 + randint(0, 1),
      items=[
        Amethyst,
        Antidote, Antidote,
        Booze,
        LovePotion,
        MusicBox,
        Topaz,
        Balloon,
        Emerald,
        Ankh,
        Elixir,
        Potion, Potion,
        Ruby,
        Berry,
        Bread, Bread,
        Cheese, Cheese,
        Fish, Fish,
        Sapphire
      ],
      seed=seed
    )
