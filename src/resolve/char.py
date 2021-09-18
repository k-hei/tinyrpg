from cores.genie import GenieCore
from cores.rogue import RogueCore
from cores.beetle import BeetleCore
from cores.mage import MageCore
from cores.husband import HusbandCore
from cores.wife import WifeCore
from cores.biped import BipedCore
from cores.knight import KnightCore
from cores.radhead import RadheadCore
from cores.mira import MiraCore
from cores.beetless import BeetlessCore
from cores.ghost import GhostCore
from cores.rat import RatCore

def resolve_char(key):
  if key == "GenieCore": return GenieCore
  if key == "RogueCore": return RogueCore
  if key == "BeetleCore": return BeetleCore
  if key == "MageCore": return MageCore
  if key == "HusbandCore": return HusbandCore
  if key == "WifeCore": return WifeCore
  if key == "BipedCore": return BipedCore
  if key == "KnightCore": return KnightCore
  if key == "RadheadCore": return RadheadCore
  if key == "MiraCore": return MiraCore
  if key == "BeetlessCore": return BeetlessCore
  if key == "GhostCore": return GhostCore
  if key == "RatCore": return RatCore
