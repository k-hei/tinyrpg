from town.areas.outskirts import OutskirtsArea
from town.areas.akimor_central import AkimorCentralArea
from town.areas.time_chamber import TimeChamberArea
from town.areas.clearing import ClearingArea
from town.areas.store import StoreArea
from town.areas.fortune import FortuneArea
from town.areas.central import CentralArea

def resolve_area(key):
  if key == "OutskirtsArea": return OutskirtsArea
  if key == "AkimorCentralArea": return AkimorCentralArea
  if key == "TimeChamberArea": return TimeChamberArea
  if key == "ClearingArea": return ClearingArea
  if key == "StoreArea": return StoreArea
  if key == "FortuneArea": return FortuneArea
  if key == "CentralArea": return CentralArea
