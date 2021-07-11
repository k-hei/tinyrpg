from dungeon.features.exitroom import ExitRoom
from dungeon.props.treasuredoor import TreasureDoor

class LockedExitRoom(ExitRoom):
  EntryDoor = TreasureDoor
