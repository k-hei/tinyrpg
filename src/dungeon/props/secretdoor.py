from dataclasses import dataclass
from dungeon.props.door import Door
from filters import replace_color

class SecretDoor(Door):
  def __init__(door, opened=False, hidden=True, *args, **kwargs):
    super().__init__(opened=opened, *args, **kwargs)
    door.hidden = hidden

  def effect(door, game, *_):
    if door.hidden:
      door.hidden = False
      game.redraw_tiles(force=True)
      return True
    else:
      return super().effect(game, *_)

  # view handled in stageview (do we need to make individual props/elems more context-aware for decentralization?)
