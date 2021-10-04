from dungeon.floors.debugfloor import DebugFloor
from dungeon.floors.floor1 import Floor1
from dungeon.floors.genericfloor import GenericFloor
from dungeon.floors.floor3 import Floor3
from dungeon.floors.floor2 import Floor2

def resolve_floor(key):
  if key == "DebugFloor": return DebugFloor
  if key == "Floor1": return Floor1
  if key == "GenericFloor": return GenericFloor
  if key == "Floor3": return Floor3
  if key == "Floor2": return Floor2
