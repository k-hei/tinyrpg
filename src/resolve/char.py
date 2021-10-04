from cores.genie import Genie
from cores.rogue import Rogue
from cores.beetle import Beetle
from cores.mage import Mage
from cores.husband import Husband
from cores.wife import Wife
from cores.biped import BipedCore
from cores.knight import Knight
from cores.radhead import Radhead
from cores.mira import MiraCore
from cores.beetless import Beetless
from cores.ghost import Ghost
from cores.rat import Rat

def resolve_char(key):
  if key == "Genie": return Genie
  if key == "Rogue": return Rogue
  if key == "Beetle": return Beetle
  if key == "Mage": return Mage
  if key == "Husband": return Husband
  if key == "Wife": return Wife
  if key == "BipedCore": return BipedCore
  if key == "Knight": return Knight
  if key == "Radhead": return Radhead
  if key == "MiraCore": return MiraCore
  if key == "Beetless": return Beetless
  if key == "Ghost": return Ghost
  if key == "Rat": return Rat
