from dungeon.actors import DungeonActor
from cores.genie import Genie as GenieCore
from colors.palette import BLACK, ORANGE

class Genie(DungeonActor):
  def __init__(genie, color=ORANGE, faction="ally", *args, **kwargs):
    super().__init__(GenieCore(color=color, faction=faction, *args, **kwargs))

  def encode(genie):
    [cell, kind, *props] = super().encode()
    props = props[0] if props else {}
    return [cell, kind, {
      **props,
      **({ "color": genie.core.color } if genie.core.color != ORANGE else {}),
      "name": genie.core.name,
    }]

  def view(genie, anims=[]):
    sprite, *_ = genie.core.view()
    return super().view([sprite, *_], anims)
