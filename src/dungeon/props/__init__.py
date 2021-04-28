from dungeon.element import DungeonElement

class Prop(DungeonElement):
  def __init__(prop, solid=True):
    super().__init__(solid)

  def effect(prop):
    pass
