from dataclasses import dataclass
from dungeon.props.door import Door
from lib.filters import replace_color

class SecretDoor(Door):
  def exists_at(stage, cell):
    return next((e for e in stage.get_elems_at(cell) if type(e) is SecretDoor and e.hidden), None)

  def __init__(door, opened=False, hidden=True, *args, **kwargs):
    super().__init__(opened=opened, *args, **kwargs)
    door.hidden = hidden

  def effect(door, game, *_):
    if door.hidden:
      door.hidden = False
      return True
    else:
      return super().effect(game, *_)

  # view handled in stageview (do we need to make individual props/elems more context-aware for decentralization?)
