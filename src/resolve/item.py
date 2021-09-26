from items.ailment.booze import Booze
from items.ailment.topaz import Topaz
from items.ailment.musicbox import MusicBox
from items.ailment.antidote import Antidote
from items.ailment.amethyst import Amethyst
from items.ailment.lovepotion import LovePotion
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

def resolve_item(key):
  if key == "Booze": return Booze
  if key == "Topaz": return Topaz
  if key == "MusicBox": return MusicBox
  if key == "Antidote": return Antidote
  if key == "Amethyst": return Amethyst
  if key == "LovePotion": return LovePotion
  if key == "Bread": return Bread
  if key == "Berry": return Berry
  if key == "Cheese": return Cheese
  if key == "Sapphire": return Sapphire
  if key == "Fish": return Fish
  if key == "Diamond": return Diamond
  if key == "Beetle": return Beetle
  if key == "AngelTears": return AngelTears
  if key == "CrownJewel": return CrownJewel
  if key == "LuckyChoker": return LuckyChoker
  if key == "RedFerrule": return RedFerrule
  if key == "Ankh": return Ankh
  if key == "Ruby": return Ruby
  if key == "Elixir": return Elixir
  if key == "Potion": return Potion
  if key == "Key": return Key
  if key == "Emerald": return Emerald
  if key == "Balloon": return Balloon
  if key == "RustyBlade": return RustyBlade
