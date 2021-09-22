from dungeon.props.treasuredoor import TreasureDoor

def on_place(room, stage):
  if not room.get_enemies(stage):
    return
  for door in room.get_doors(stage):
    if isinstance(door, TreasureDoor):
      door.lock()
