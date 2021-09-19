from dungeon.props.door import Door, SpriteMap

class TreasureDoor(Door):
  sprites = SpriteMap(
    closed="door_treasure",
    opened="door_treasure_open",
    opening_frames=[
      "door_treasure",
      "door_treasure_opening",
      "door_treasure_open"
    ]
  )
