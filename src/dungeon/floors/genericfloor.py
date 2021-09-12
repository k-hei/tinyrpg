from random import randint
from dungeon.floors import Floor
from dungeon.features.vertroom import VerticalRoom
from dungeon.features.irregularroom import IrregularRoom
from dungeon.features.oasisroom import OasisRoom
from dungeon.features.raretreasureroom import RareTreasureRoom
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
from skills.weapon.longinus import Longinus

class GenericFloor(Floor):
  def generate(store):
    entry_room = VerticalRoom(size=(3, 4), degree=2)
    return gen_floor(
      size=(27, 27),
      features=[
        entry_room,
        *[IrregularRoom() for _ in range(randint(0, 2))]
        *([OasisRoom()] if randint(1, 5) == 1 else []),
        *(Longinus not in store.skills and randint(1, 2) == 1 and [RareTreasureRoom()] or []),
      ],
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
      ])
