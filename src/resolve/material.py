from items.ailment.booze import Booze
from items.ailment.topaz import Topaz
from items.ailment.musicbox import MusicBox
from items.ailment.antidote import Antidote
from items.ailment.amethyst import Amethyst
from items.ailment.lovepotion import LovePotion
from items.sp.vino import Vino
from items.sp.bread import Bread
from items.sp.berry import Berry
from items.sp.cheese import Cheese
from items.sp.sapphire import Sapphire
from items.sp.fish import Fish
from items.materials.diamond import Diamond
from items.materials.beetle import Beetle
from items.materials.angeltears import AngelTears
from items.materials.crownjewel import CrownJewel
from items.materials.luckychoker import LuckyChoker
from items.materials.redferrule import RedFerrule
from items.hp.ankh import Ankh
from items.hp.ruby import Ruby
from items.hp.elixir import Elixir
from items.hp.potion import Potion
from items.dungeon.key import Key
from items.dungeon.emerald import Emerald
from items.dungeon.balloon import Balloon
from items.equipment.rustyblade import RustyBlade
from dungeon.actors.genie import Genie
from dungeon.actors.mummy import Mummy
from dungeon.actors.mageclone import MageClone
from dungeon.actors.npc import Npc
from dungeon.actors.skeleton import Skeleton
from dungeon.actors.eyeball import Eyeball
from dungeon.actors.beetle import Beetle
from dungeon.actors.mage import Mage
from dungeon.actors.mimic import Mimic
from dungeon.actors.knight import Knight
from dungeon.actors.mushroom import Mushroom
from dungeon.actors.guard import GuardActor
from dungeon.actors.ghost import Ghost

def resolve_material(material):
  if material is Diamond: return None
  if material is Beetle: return None
  if material is AngelTears: return Eyeball
  if material is CrownJewel: return Mummy
  if material is LuckyChoker: return Ghost
  if material is RedFerrule: return Mushroom
