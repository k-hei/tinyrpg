from dungeon.floors import Floor
from dungeon.gen import gen_floor, gen_enemy, FloorGraph
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
  def generate(store):
    return gen_floor(size=(27, 27), items=[
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
    ])
