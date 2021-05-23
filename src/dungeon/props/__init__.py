from dungeon.element import DungeonElement

class Prop(DungeonElement):
  def __init__(prop, solid=True, opaque=False):
    super().__init__(solid, opaque)

  def effect(prop, game):
    pass
