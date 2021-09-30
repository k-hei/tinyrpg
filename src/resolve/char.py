from cores.beetle import Beetle
from cores.beetless import Beetless
from cores.biped import BipedCore
from cores.genie import Genie
from cores.ghost import Ghost
from cores.husband import Husband
from cores.knight import Knight
from cores.mage import Mage
from cores.mira import MiraCore
from cores.radhead import Radhead
from cores.rat import Rat
from cores.rogue import Rogue
from cores.wife import Wife

def resolve_char(key):
  if key == "Beetle": return Beetle
  if key == "Beetless": return Beetless
  if key == "BipedCore": return BipedCore
  if key == "Genie": return Genie
  if key == "Ghost": return Ghost
  if key == "Husband": return Husband
  if key == "Knight": return Knight
  if key == "Mage": return Mage
  if key == "MiraCore": return MiraCore
  if key == "Radhead": return Radhead
  if key == "Rat": return Rat
  if key == "Rogue": return Rogue
  if key == "Wife": return Wife
