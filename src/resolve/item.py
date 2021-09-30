from items.ailment.amethyst import Amethyst
from items.ailment.antidote import Antidote
from items.ailment.booze import Booze
from items.ailment.lovepotion import LovePotion
from items.ailment.musicbox import MusicBox
from items.ailment.topaz import Topaz
from items.dungeon.balloon import Balloon
from items.dungeon.emerald import Emerald
from items.dungeon.key import Key
from items.equipment.rustyblade import RustyBlade
from items.hp.ankh import Ankh
from items.hp.elixir import Elixir
from items.hp.potion import Potion
from items.hp.ruby import Ruby
from items.materials.angeltears import AngelTears
from items.materials.beetle import Beetle
from items.materials.crownjewel import CrownJewel
from items.materials.diamond import Diamond
from items.materials.luckychoker import LuckyChoker
from items.materials.redferrule import RedFerrule
from items.sp.berry import Berry
from items.sp.bread import Bread
from items.sp.cheese import Cheese
from items.sp.fish import Fish
from items.sp.sapphire import Sapphire

def resolve_item(key):
  if key == "Amethyst": return Amethyst
  if key == "Antidote": return Antidote
  if key == "Booze": return Booze
  if key == "LovePotion": return LovePotion
  if key == "MusicBox": return MusicBox
  if key == "Topaz": return Topaz
  if key == "Balloon": return Balloon
  if key == "Emerald": return Emerald
  if key == "Key": return Key
  if key == "RustyBlade": return RustyBlade
  if key == "Ankh": return Ankh
  if key == "Elixir": return Elixir
  if key == "Potion": return Potion
  if key == "Ruby": return Ruby
  if key == "AngelTears": return AngelTears
  if key == "Beetle": return Beetle
  if key == "CrownJewel": return CrownJewel
  if key == "Diamond": return Diamond
  if key == "LuckyChoker": return LuckyChoker
  if key == "RedFerrule": return RedFerrule
  if key == "Berry": return Berry
  if key == "Bread": return Bread
  if key == "Cheese": return Cheese
  if key == "Fish": return Fish
  if key == "Sapphire": return Sapphire
