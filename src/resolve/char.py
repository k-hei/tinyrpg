from cores.mook import Mook
from cores.genie import Genie
from cores.rogue import Rogue
from cores.beetle import Beetle
from cores.mage import Mage
from cores.bunny import Bunny
from cores.husband import Husband
from cores.boar import Boar
from cores.wife import Wife
from cores.biped import BipedCore
from cores.knight import Knight
from cores.radhead import Radhead
from cores.mouse import Mouse
from cores.mira import MiraCore
from cores.beetless import Beetless
from cores.ghost import Ghost
from cores.rat import Rat

def resolve_char(key):
  if key == "Mook": return Mook
  if key == "Genie": return Genie
  if key == "Rogue": return Rogue
  if key == "Beetle": return Beetle
  if key == "Mage": return Mage
  if key == "Bunny": return Bunny
  if key == "Husband": return Husband
  if key == "Boar": return Boar
  if key == "Wife": return Wife
  if key == "BipedCore": return BipedCore
  if key == "Knight": return Knight
  if key == "Radhead": return Radhead
  if key == "Mouse": return Mouse
  if key == "MiraCore": return MiraCore
  if key == "Beetless": return Beetless
  if key == "Ghost": return Ghost
  if key == "Rat": return Rat
