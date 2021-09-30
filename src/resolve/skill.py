from skills.ailment.exoculo import Exoculo
from skills.ailment.somnus import Somnus
from skills.ailment.steal import Steal
from skills.ailment.virus import Virus
from skills.armor.buckler import Buckler
from skills.armor.hpup import HpUp
from skills.attack.blitzritter import Blitzritter
from skills.attack.clawrush import ClawRush
from skills.attack.cleave import Cleave
from skills.attack.helmsplitter import HelmSplitter
from skills.attack.rendinggale import RendingGale
from skills.attack.shieldbash import ShieldBash
from skills.field.detectmana import DetectMana
from skills.magic.accerso import Accerso
from skills.magic.congelatio import Congelatio
from skills.magic.fulgur import Fulgur
from skills.magic.glacio import Glacio
from skills.magic.hirudo import Hirudo
from skills.magic.ignis import Ignis
from skills.magic.vortex import Vortex
from skills.support.anastasis import Anastasis
from skills.support.counter import Counter
from skills.support.sana import Sana
from skills.weapon.broadsword import BroadSword
from skills.weapon.caladbolg import Caladbolg
from skills.weapon.club import Club
from skills.weapon.cudgel import Cudgel
from skills.weapon.longinus import Longinus
from skills.weapon.mjolnir import Mjolnir
from skills.weapon.rare import RareWeapon
from skills.weapon.rustyblade import RustyBlade
from skills.weapon.stick import Stick
from skills.weapon.tackle import Tackle

def resolve_skill(key):
  if key == "Exoculo": return Exoculo
  if key == "Somnus": return Somnus
  if key == "Steal": return Steal
  if key == "Virus": return Virus
  if key == "Buckler": return Buckler
  if key == "HpUp": return HpUp
  if key == "Blitzritter": return Blitzritter
  if key == "ClawRush": return ClawRush
  if key == "Cleave": return Cleave
  if key == "HelmSplitter": return HelmSplitter
  if key == "RendingGale": return RendingGale
  if key == "ShieldBash": return ShieldBash
  if key == "DetectMana": return DetectMana
  if key == "Accerso": return Accerso
  if key == "Congelatio": return Congelatio
  if key == "Fulgur": return Fulgur
  if key == "Glacio": return Glacio
  if key == "Hirudo": return Hirudo
  if key == "Ignis": return Ignis
  if key == "Vortex": return Vortex
  if key == "Anastasis": return Anastasis
  if key == "Counter": return Counter
  if key == "Sana": return Sana
  if key == "BroadSword": return BroadSword
  if key == "Caladbolg": return Caladbolg
  if key == "Club": return Club
  if key == "Cudgel": return Cudgel
  if key == "Longinus": return Longinus
  if key == "Mjolnir": return Mjolnir
  if key == "RareWeapon": return RareWeapon
  if key == "RustyBlade": return RustyBlade
  if key == "Stick": return Stick
  if key == "Tackle": return Tackle
