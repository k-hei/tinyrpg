from dungeon.props.door import Door, SpriteMap
from contexts.prompt import PromptContext, Choice

class BattleDoor(Door):
  sprites = SpriteMap(
    closed="door_battle",
    opened="door_battle_open",
    opening_frames=["door_battle", "door_battle_opening", "door_battle_open"]
  )

  def effect(door, game, *args, **kwargs):
    effect = super().effect
    if door.locked:
      return effect(game, *args, **kwargs)
    elif not door.opened:
      game.open(PromptContext("Open the door?", [
        Choice("Yes"),
        Choice("No", closing=True)
      ], on_close=lambda choice: (
        choice and choice.text == "Yes" and effect(game, *args, **kwargs)
      )))
      return True
