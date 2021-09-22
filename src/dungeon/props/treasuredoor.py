from dungeon.props.door import Door, SpriteMap
from colors.palette import DARKBLUE, SAFFRON
from filters import replace_color

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

  def __init__(door, opened=False, locked=False, *args, **kwargs):
    super().__init__(opened=opened, locked=(not opened or locked), *args, **kwargs)

  def view(door, anims):
    sprites = super().view(anims)
    if not door.locked and sprites:
      sprite = sprites[0]
      sprite.image = replace_color(sprite.image, SAFFRON, DARKBLUE)
    return sprites
