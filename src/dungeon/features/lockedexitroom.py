from dungeon.features.exitroom import ExitRoom
from dungeon.props.raretreasuredoor import RareTreasureDoor

class LockedExitRoom(ExitRoom):
  EntryDoor = RareTreasureDoor
